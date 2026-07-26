package com.notestream.notestream_api.integration;

import java.util.List;

public record EmbedResponse(List<List<Float>> embeddings) {}
