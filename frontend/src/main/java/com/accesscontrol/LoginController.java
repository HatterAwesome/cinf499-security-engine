package com.accesscontrol;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller // Handles webpage requests
public class LoginController {

    @GetMapping("/login") // Runs when someone visits /login
    public String login() {

        // Display login.html from the templates folder
        return "login";
    }
}
