package com.notestream.notestream_api.integration;

import java.util.List;

public record AskResponse(
    String answer,
    List<Integer> citations
) {}