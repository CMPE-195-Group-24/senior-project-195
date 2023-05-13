//
//  UserView.swift
//  NFCReader
//
//  Created by Ross Nikolai Montepalco on 5/9/23.
//

import SwiftUI

struct UserView: View {
    @State var contentTitle = ""
    
    var body: some View {
        NavigationStack {
            Divider()
                .frame(height: 170, alignment: .top)
                .background(Color.blue.opacity(2))
                .clipShape(RoundShape(corners: [.bottomRight]))
                .frame(height: 200, alignment: .top)
                .background(Color.blue.opacity(0.5))
                .clipShape(RoundShape(corners: [.bottomRight]))
                .offset(y: -10)
                .ignoresSafeArea()
            TabView {
                CardView()
                .tabItem {
                    Image(systemName: "lock.rectangle.stack")
                    Text("Digital Cards")
                        .background(Color(UIColor.systemBackground))
                }
                .onAppear(){
                    contentTitle = "Digital Cards"
                }
                ProfileView()
                .tabItem {
                    Image(systemName: "person.crop.circle")
                    Text("Profile")
                        .background(Color(UIColor.systemBackground))
                }
                .onAppear(){
                    contentTitle = "Profile"
                }
            }
            .navigationTitle(contentTitle)
            .frame(height: 700)
            .offset(y: -50)
        }
    }
}

struct RoundShape: Shape {
    var corners: UIRectCorner
    
    func path(in rect: CGRect) -> Path {
        let path = UIBezierPath(roundedRect: rect, byRoundingCorners: corners, cornerRadii: CGSize(width: 80, height: 80))
        
        return Path(path.cgPath)
    }
}

struct UserView_Previews: PreviewProvider {
    static var previews: some View {
        UserView()
    }
}
