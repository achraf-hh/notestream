package com.notestream.notestream_api.integration;

import org.springframework.http.MediaType;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.net.http.HttpClient;
import java.util.List;

@Component
public class AiClient {

    private final RestClient restClient;

    public AiClient(@Value("${ai.service.url}") String aiServiceUrl) {
        HttpClient httpClient = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .build();

        this.restClient = RestClient.builder()
                .baseUrl(aiServiceUrl)
                .requestFactory(new JdkClientHttpRequestFactory(httpClient))
                .build();
    }


    public List<float[]> embed(List<String> texts) {
        EmbedResponse response = restClient.post()
                .uri("/embed")
                .contentType(MediaType.APPLICATION_JSON)
                .body(new EmbedRequest(texts))
                .retrieve()
                .body(EmbedResponse.class);

        if (response == null || response.embeddings() == null) {
            throw new IllegalStateException("AI service returned no embeddings");
        }

        if (response.embeddings().size() != texts.size()) {
            throw new IllegalStateException("AI service returned an unexpected number of embeddings");
        }

        return response.embeddings().stream()
                .map(this::toPrimitiveArray)
                .toList();
    }


    public AskResponse ask(String question, List<String> contextChunks) {
        AskResponse response = restClient.post()
                .uri("/ask")
                .contentType(MediaType.APPLICATION_JSON)
                .body(new AskRequest(question, contextChunks))
                .retrieve()
                .body(AskResponse.class);

        if (response == null) {
            throw new IllegalStateException("AI service returned no answer");
        }

        return response;
    }

    private float[] toPrimitiveArray(List<Float> embedding) {
        float[] values = new float[embedding.size()];
        for (int i = 0; i < embedding.size(); i++) {
            values[i] = embedding.get(i);
        }
        return values;
    }
}
