package com.example.docmindAI.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class AIResponse {
    private String request_id;
    private String answer;
    private List<String> sources;
    private String status;
}
