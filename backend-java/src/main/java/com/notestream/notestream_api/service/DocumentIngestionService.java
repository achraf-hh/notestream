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
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

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
        final Document savedDocument = documentRepository.save(document);

        // 3. Stream text chunks directly from the PDF and persist as we go
        final AtomicInteger position = new AtomicInteger(0);
        final List<Chunk> savedChunks = new ArrayList<>();
        pdfParsingService.streamChunks(file, chunkText ->
                savedChunks.add(chunkRepository.save(new Chunk(
                        chunkText,
                        position.getAndIncrement(),
                        savedDocument
                ))));

        // 4. Generate embeddings for similarity search and persist them on the saved chunks.
        if (!savedChunks.isEmpty()) {
            List<float[]> embeddings = aiClient.embed(savedChunks.stream()
                    .map(Chunk::getContent)
                    .toList());

            if (embeddings.size() != savedChunks.size()) {
                throw new IllegalStateException("Embedding count does not match saved chunk count");
            }

            for (int i = 0; i < savedChunks.size(); i++) {
                savedChunks.get(i).setEmbedding(embeddings.get(i));
            }

            chunkRepository.saveAll(savedChunks);
        }

        return savedDocument;
    }

    public Document getDocument(Long documentId) {
        return documentRepository.findById(documentId)
                .orElseThrow(() -> new EntityNotFoundException("Document not found: " + documentId));
    }

    public List<Document> getDocumentsByCourse(Long courseId) {
        return documentRepository.findByCourseId(courseId);
    }
}
