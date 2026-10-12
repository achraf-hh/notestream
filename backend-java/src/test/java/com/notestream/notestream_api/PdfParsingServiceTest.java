package com.notestream.notestream_api;

import com.notestream.notestream_api.service.PdfParsingService;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.font.PDType1Font;
import org.apache.pdfbox.pdmodel.font.Standard14Fonts;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockMultipartFile;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

class PdfParsingServiceTest {

    private final PdfParsingService pdfParsingService = new PdfParsingService();

    @Test
    void streamChunksSplitsAMultiPagePdfIntoOverlappingChunks() throws IOException {
        List<String> sentences = new ArrayList<>();
        for (int i = 1; i <= 60; i++) {
            sentences.add("Sentence " + i + " describes how replicas agree on the log.");
        }
        MockMultipartFile pdf = new MockMultipartFile(
                "file", "paper.pdf", "application/pdf", pdfWithPages(sentences.subList(0, 30), sentences.subList(30, 60)));

        List<String> chunks = new ArrayList<>();
        pdfParsingService.streamChunks(pdf, chunks::add);

        assertThat(chunks).hasSizeGreaterThan(1);
        // Chunks target 500 characters but may extend to the next sentence end within the overlap window.
        assertThat(chunks).allSatisfy(chunk -> assertThat(chunk.length()).isLessThanOrEqualTo(550));
        String joined = String.join(" ", chunks);
        assertThat(sentences).allSatisfy(sentence -> assertThat(joined).contains(sentence));
        for (int i = 1; i < chunks.size(); i++) {
            String previous = chunks.get(i - 1);
            String overlap = previous.substring(previous.length() - 40);
            assertThat(chunks.get(i)).contains(overlap);
        }
    }

    @SafeVarargs
    private static byte[] pdfWithPages(List<String>... pages) throws IOException {
        try (PDDocument document = new PDDocument(); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            for (List<String> lines : pages) {
                PDPage page = new PDPage();
                document.addPage(page);
                try (PDPageContentStream content = new PDPageContentStream(document, page)) {
                    content.beginText();
                    content.setFont(new PDType1Font(Standard14Fonts.FontName.HELVETICA), 10);
                    content.setLeading(14);
                    content.newLineAtOffset(50, 750);
                    for (String line : lines) {
                        content.showText(line);
                        content.newLine();
                    }
                    content.endText();
                }
            }
            document.save(out);
            return out.toByteArray();
        }
    }
}
