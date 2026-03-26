package com.example.docmindAI.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class AIRequest {
    private String request_id;
    private String user_id;
    private String conversation_id;
    private String question;
}
