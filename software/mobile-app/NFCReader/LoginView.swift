//
//  LoginView.swift
//  NFCReader
//
//  Created by Ross Nikolai Montepalco on 4/30/23.
//

import SwiftUI
import FirebaseAuth

struct LoginView: View {
    // State Variables
    @State private var email = ""
    @State private var password = ""
    @State private var validLogin = false
    
    var body: some View {
        NavigationView {
            ZStack {
                // Background
                Color.blue
                    .ignoresSafeArea()
                Circle()
                    .scale(1.7)
                    .foregroundColor(.white.opacity(0.15))
                Circle()
                    .scale(1.35)
                    .foregroundColor(.white)
                
                VStack {
                    // Login credentials
                    Text("NFC Reader")
                        .foregroundColor(Color.black)
                        .font(.largeTitle)
                        .bold()
                        .padding()
                    TextField("Email", text: $email)
                        .foregroundColor(Color.black)
                        .padding()
                        .frame(width: 300, height: 50)
                        .background(Color.black.opacity(0.05))
                        .cornerRadius(10)
                    SecureField("Password", text: $password)
                        .foregroundColor(Color.black)
                        .padding()
                        .frame(width: 300, height: 50)
                        .background(Color.black.opacity(0.05))
                        .cornerRadius(10)
                    
                    // TODO: Display wrong email/password message after failed login attempt.
                    
                    /*
                    Button("Login") {
                        login()
                    }
                        .foregroundColor(.white)
                        .frame(width: 300, height: 50)
                        .background(Color.blue)
                        .cornerRadius(10)
                     */
                    
                    NavigationLink {
                        UserView().navigationBarBackButtonHidden(true)
                    } label: {
                        Rectangle()
                            .frame(width: 300, height: 50)
                            .background(Color.black.opacity(0.05))
                            .cornerRadius(10)
                            .overlay(Text("Login")
                                .foregroundColor(.white))
                    }
                    
                }
            }
        }
    }

    
    func login() {
        Auth.auth().signIn(withEmail: email, password: password) { (result, error) in
            if error != nil {
                print(error?.localizedDescription ?? "")
            } else {
                print("success")
                validLogin = true;
            }
        }
    }
     
    
}

struct LoginView_Previews: PreviewProvider {
    static var previews: some View {
        LoginView()
    }
}
