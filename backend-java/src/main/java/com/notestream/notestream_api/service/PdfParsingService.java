package com.notestream.notestream_api.service;

import org.apache.pdfbox.Loader;
import org.apache.pdfbox.io.RandomAccessReadBuffer;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

@Service
public class PdfParsingService {

    private static final int CHUNK_SIZE = 500;
    private static final int CHUNK_OVERLAP = 50;
    private static final long MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

    public String extractText(MultipartFile file) throws IOException {
        // Validate file size
        if (file.getSize() > MAX_FILE_SIZE) {
            throw new IOException("File too large. Maximum size is 10 MB.");
        }

        try (PDDocument document = Loader.loadPDF(new RandomAccessReadBuffer(file.getInputStream()))) {
            PDFTextStripper stripper = new PDFTextStripper();
            return stripper.getText(document);
        }
    }

    public int getPageCount(MultipartFile file) throws IOException {
        try (PDDocument document = Loader.loadPDF(new RandomAccessReadBuffer(file.getInputStream()))) {
            return document.getNumberOfPages();
        }
    }

    public List<String> splitIntoChunks(String text) {
        List<String> chunks = new ArrayList<>();

        if (text == null || text.isEmpty()) {
            return chunks;
        }

        text = text.replaceAll("\\s+", " ").trim();

        int start = 0;
        while (start < text.length()) {
            int end = Math.min(start + CHUNK_SIZE, text.length());

            if (end < text.length()) {
                int lastPeriod = text.lastIndexOf(". ", end);
                int lastQuestion = text.lastIndexOf("? ", end);
                int lastExclamation = text.lastIndexOf("! ", end);
                
                int bestBreak = Math.max(lastPeriod, Math.max(lastQuestion, lastExclamation));
                
                if (bestBreak > start + CHUNK_SIZE / 2) {
                    end = bestBreak + 1;
                }
            }

            String chunk = text.substring(start, end).trim();
            if (!chunk.isEmpty()) {
                chunks.add(chunk);
            }

            start = end - CHUNK_OVERLAP;
            if (start < 0) start = 0;
            
            if (start >= text.length() - 1) break;
        }

        return chunks;
    }

    /**
     * Stream chunked text from a PDF to the provided consumer, avoiding full in-memory accumulation.
     */
    public void streamChunks(MultipartFile file, Consumer<String> chunkConsumer) throws IOException {
        // Validate file size up front to prevent runaway memory usage
        if (file.getSize() > MAX_FILE_SIZE) {
            throw new IOException("File too large. Maximum size is 10 MB.");
        }

        try (PDDocument document = Loader.loadPDF(new RandomAccessReadBuffer(file.getInputStream()))) {
            PDFTextStripper stripper = new PDFTextStripper();
            StringBuilder buffer = new StringBuilder();

            int totalPages = document.getNumberOfPages();
            for (int page = 1; page <= totalPages; page++) {
                stripper.setStartPage(page);
                stripper.setEndPage(page);

                String pageText = normalizeWhitespace(stripper.getText(document));
                if (!pageText.isEmpty()) {
                    buffer.append(pageText).append(" ");
                    emitChunks(buffer, chunkConsumer);
                }
            }

            // Flush any remaining text as the last chunk
            if (buffer.length() > 0) {
                String tail = buffer.toString().trim();
                if (!tail.isEmpty()) {
                    chunkConsumer.accept(tail);
                }
            }
        }
    }

    private void emitChunks(StringBuilder buffer, Consumer<String> chunkConsumer) {
        while (buffer.length() >= CHUNK_SIZE) {
            int end = Math.min(CHUNK_SIZE, buffer.length());
            if (buffer.length() > CHUNK_SIZE) {
                int bestBreak = findBestBreak(buffer, end);
                if (bestBreak >= end / 2) {
                    end = bestBreak + 1;
                }
            }

            String chunk = buffer.substring(0, end).trim();
            if (!chunk.isEmpty()) {
                chunkConsumer.accept(chunk);
            }

            int deleteUntil = Math.max(0, end - CHUNK_OVERLAP);
            buffer.delete(0, deleteUntil);
        }
    }

    private int findBestBreak(CharSequence text, int searchLimit) {
        int limit = Math.min(searchLimit + CHUNK_OVERLAP, text.length());
        int lastPeriod = lastIndexOf(text, ". ", limit);
        int lastQuestion = lastIndexOf(text, "? ", limit);
        int lastExclamation = lastIndexOf(text, "! ", limit);
        return Math.max(lastPeriod, Math.max(lastQuestion, lastExclamation));
    }

    private int lastIndexOf(CharSequence text, String needle, int limit) {
        int needleLen = needle.length();
        for (int i = Math.min(limit - needleLen, text.length() - needleLen); i >= 0; i--) {
            if (text.charAt(i) == needle.charAt(0)) {
                boolean match = true;
                for (int j = 1; j < needleLen; j++) {
                    if (text.charAt(i + j) != needle.charAt(j)) {
                        match = false;
                        break;
                    }
                }
                if (match) {
                    return i;
                }
            }
        }
        return -1;
    }

    private String normalizeWhitespace(String text) {
        if (text == null || text.isEmpty()) {
            return "";
        }
        return text.replaceAll("\\s+", " ").trim();
    }
}
