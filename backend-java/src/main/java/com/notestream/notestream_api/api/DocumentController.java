package com.notestream.notestream_api.api;

import com.notestream.notestream_api.domain.model.Chunk;
import com.notestream.notestream_api.domain.model.Document;
import com.notestream.notestream_api.service.DocumentIngestionService;
import com.notestream.notestream_api.domain.repository.DocumentRepository;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class DocumentController {

    private static final long MAX_UPLOAD_BYTES = 10 * 1024 * 1024; // 10 MB
    private final DocumentIngestionService documentIngestionService;
    private final DocumentRepository documentRepository;

    public DocumentController(DocumentIngestionService documentIngestionService, DocumentRepository documentRepository) {
        this.documentIngestionService = documentIngestionService;
        this.documentRepository = documentRepository;
    }

    @PostMapping("/courses/{courseId}/documents")
    public ResponseEntity<?> uploadDocument(
            @PathVariable Long courseId,
            @RequestParam("file") MultipartFile file) {
        
        // Validate file
        if (file.isEmpty()) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "File is empty"));
        }

        String contentType = file.getContentType();
        if (contentType == null || !contentType.toLowerCase().startsWith("application/pdf")) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "Only PDF files are allowed"));
        }

        if (file.getSize() > MAX_UPLOAD_BYTES) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "File too large. Maximum size is 10 MB."));
        }

        try {
            Document document = documentIngestionService.ingestDocument(courseId, file);
            
            return ResponseEntity.status(HttpStatus.CREATED).body(Map.of(
                    "id", document.getId(),
                    "filename", document.getFilename(),
                    "fileSize", document.getFileSize(),
                    "uploadedAt", document.getUploadedAt().toString(),
                    "message", "Document uploaded and processed successfully"
            ));
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Failed to process PDF: " + e.getMessage()));
        }
    }

    @GetMapping("/courses/{courseId}/documents")
    public ResponseEntity<List<Document>> getDocumentsByCourse(@PathVariable Long courseId) {
        List<Document> documents = documentIngestionService.getDocumentsByCourse(courseId);
        return ResponseEntity.ok(documents);
    }

    @GetMapping("/documents/{documentId}/chunks")
public ResponseEntity<List<Chunk>> getChunks(@PathVariable Long documentId) {
    Document document = documentRepository.findById(documentId)
        .orElseThrow(() -> new RuntimeException("Document not found"));
    return ResponseEntity.ok(document.getChunks());
}

    @GetMapping("/documents/{documentId}")
    public ResponseEntity<Document> getDocument(@PathVariable Long documentId) {
        Document document = documentIngestionService.getDocument(documentId);
        return ResponseEntity.ok(document);
    }
}
