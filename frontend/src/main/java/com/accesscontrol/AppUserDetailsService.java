package com.accesscontrol;

import com.accesscontrol.model.AppUser;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

// Loads application accounts from MongoDB for Spring Security.
@Service
public class AppUserDetailsService implements UserDetailsService {

    private final AppUserRepository userRepository;

    public AppUserDetailsService(AppUserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Override
    public UserDetails loadUserByUsername(String username)
            throws UsernameNotFoundException {

        AppUser appUser = userRepository.findByUsername(username)
                .orElseThrow(() ->
                        new UsernameNotFoundException("User not found"));

        return User.withUsername(appUser.getUsername())
                .password(appUser.getPassword())
                .authorities(appUser.getRole())
                .build();
    }
}
