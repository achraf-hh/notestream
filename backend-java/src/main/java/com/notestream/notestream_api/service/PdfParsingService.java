package com.notestream.notestream_api.service;

import org.apache.pdfbox.Loader;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

@Service
public class PdfParsingService {

    private static final int CHUNK_SIZE = 500;
    private static final int CHUNK_OVERLAP = 50;

    public String extractText(MultipartFile file) throws IOException {
        try (PDDocument document = Loader.loadPDF(file.getBytes())) {
            PDFTextStripper stripper = new PDFTextStripper();
            return stripper.getText(document);
        }
    }

    public int getPageCount(MultipartFile file) throws IOException {
        try (PDDocument document = Loader.loadPDF(file.getBytes())) {
            return document.getNumberOfPages();
        }
    }

    public List<String> splitIntoChunks(String text) {
        List<String> chunks = new ArrayList<>();

        if (text == null || text.isEmpty()) {
            return chunks;
        }

        // Clean the text: normalize whitespace
        text = text.replaceAll("\\s+", " ").trim();

        int start = 0;
        while (start < text.length()) {
            int end = Math.min(start + CHUNK_SIZE, text.length());

            // Try to break at a sentence boundary (., !, ?)
            if (end < text.length()) {
                int lastPeriod = text.lastIndexOf(". ", end);
                int lastQuestion = text.lastIndexOf("? ", end);
                int lastExclamation = text.lastIndexOf("! ", end);
                
                int bestBreak = Math.max(lastPeriod, Math.max(lastQuestion, lastExclamation));
                
                // Only use the break if it's within reasonable range
                if (bestBreak > start + CHUNK_SIZE / 2) {
                    end = bestBreak + 1;
                }
            }

            String chunk = text.substring(start, end).trim();
            if (!chunk.isEmpty()) {
                chunks.add(chunk);
            }

            // Move start position with overlap
            start = end - CHUNK_OVERLAP;
            if (start < 0) start = 0;
            
            // Prevent infinite loop
            if (start >= text.length() - 1) break;
        }

        return chunks;
    }
}