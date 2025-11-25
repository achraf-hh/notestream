package com.notestream.notestream_api.service;

import com.notestream.notestream_api.domain.model.Chunk;
import com.notestream.notestream_api.domain.model.Course;
import com.notestream.notestream_api.domain.model.Document;
import com.notestream.notestream_api.domain.repository.ChunkRepository;
import com.notestream.notestream_api.domain.repository.CourseRepository;
import com.notestream.notestream_api.domain.repository.DocumentRepository;
import com.notestream.notestream_api.integration.AiClient;
import jakarta.persistence.EntityNotFoundException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

@Service
public class DocumentIngestionService {

    private final PdfParsingService pdfParsingService;
    private final CourseRepository courseRepository;
    private final DocumentRepository documentRepository;
    private final ChunkRepository chunkRepository;
    private final AiClient aiClient;

    public DocumentIngestionService(
            PdfParsingService pdfParsingService,
            CourseRepository courseRepository,
            DocumentRepository documentRepository,
            ChunkRepository chunkRepository,
            AiClient aiClient) {
        this.pdfParsingService = pdfParsingService;
        this.courseRepository = courseRepository;
        this.documentRepository = documentRepository;
        this.chunkRepository = chunkRepository;
        this.aiClient = aiClient;
    }

    @Transactional
    public Document ingestDocument(Long courseId, MultipartFile file) throws IOException {
        // 1. Find the course
        Course course = courseRepository.findById(courseId)
                .orElseThrow(() -> new EntityNotFoundException("Course not found: " + courseId));

        // 2. Create document entity
        Document document = new Document(
                file.getOriginalFilename(),
                file.getContentType(),
                file.getSize(),
                course
        );
        document = documentRepository.save(document);

        // 3. Extract text from PDF
        String text = pdfParsingService.extractText(file);

        // 4. Split into chunks
        List<String> chunkTexts = pdfParsingService.splitIntoChunks(text);

        // 5. Create chunk entities (without embeddings for now)
        for (int i = 0; i < chunkTexts.size(); i++) {
            Chunk chunk = new Chunk(chunkTexts.get(i), i, document);
            chunkRepository.save(chunk);
        }

        // TODO: Step 4 - Call aiClient.embed() to get embeddings
        // List<float[]> embeddings = aiClient.embed(chunkTexts);
        // Then update each chunk with its embedding

        return document;
    }

    public Document getDocument(Long documentId) {
        return documentRepository.findById(documentId)
                .orElseThrow(() -> new EntityNotFoundException("Document not found: " + documentId));
    }

    public List<Document> getDocumentsByCourse(Long courseId) {
        return documentRepository.findByCourseId(courseId);
    }
}