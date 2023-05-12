//
//  ProfileView.swift
//  Apple NFC app test
//
//  Created by Blake Huynh on 4/20/23.
//

import SwiftUI

struct ProfileView: View {
    @State var contentTitle = "Profile"
    
    var body: some View {
        ScrollView(.vertical, showsIndicators: false) {
            VStack {
                HStack(spacing: 15) {
                    Image(systemName: "person.crop.circle")
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(width: 100, height: 100, alignment: .topLeading)
                        .clipShape(Circle())
                    
                    VStack() {
                        Text("Group 24") // can replace with a username for fun
                            .font(.title2)
                            .fontWeight(.semibold)
                            .hAlign(.leading)
                        
                        Text("This is Group 24's IOS application for the Senior Design Project") //replace with fake bio
                            .font(.caption)
                            .foregroundColor(.gray)
                            .lineLimit(3)
                        
                    }
                }
                Text("Links")
                    .font(.title3)
                    .fontWeight(.semibold)
                    .foregroundColor(.black)
                    .hAlign(.leading)
                    .padding(.vertical, 15)
                    .padding(.horizontal, 15)
                
            }
        }
        .padding()
        .refreshable{}
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Menu {
                    NavigationLink {
                        LoginView().navigationBarBackButtonHidden(true)
                    } label: {
                        Text("Logout")
                    }
                    Button("Delete Account", role: .destructive, action: deleteAcc)
                } label: {
                    Image(systemName: "ellipsis")
                        .rotationEffect(.init(degrees: 90))
                        .tint(.black)
                        .scaleEffect(0.8)
                }
            }
        }
    }
    
    
    func logOutuser() {
//        try Auth.auth().signOut()
//        logStatus = false
    }
    
    func deleteAcc() {
        //task {
//            guard let userUID = Auth.auth().currentuser?.uid //else{return}
     //   }
    }
}

struct ProfileView_Previews: PreviewProvider {
    static var previews: some View {
        ProfileView()
    }
}
