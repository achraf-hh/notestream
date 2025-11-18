package com.notestream.notestream_api.integration;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.List;

@Component
public class AiClient {

    private final RestClient restClient;

    public AiClient(@Value("${ai.service.url}") String aiServiceUrl) {
        this.restClient = RestClient.builder()
                .baseUrl(aiServiceUrl)
                .build();
    }


    public List<float[]> embed(List<String> texts) {
        // Stub - will call POST /embed on Python service
        throw new UnsupportedOperationException("AI service not implemented yet");
    }


    public String ask(String question, List<String> contextChunks) {

        throw new UnsupportedOperationException("AI service not implemented yet");
    }
}
