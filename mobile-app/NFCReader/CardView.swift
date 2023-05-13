//
//  CardView.swift
//  NFCReader
//
//  Created by Ross Nikolai Montepalco on 4/30/23.
//

import SwiftUI
import CoreNFC
import LocalAuthentication

struct CardView: View {
    @State var ID1 = "c7604df629d74f7e9e27ab9730035e78"
    @State var ID2 = "it does not work"
    @State var ID3 = "939b50100cc144c987460c00f2904235"
    @State var writer = NFCReader()
    @State private var text = "Locked"
    @State var contentTitle = "Digital Cards"
    @State private var animateGradient: Bool = false
    
    var body: some View {
        ScrollView(.vertical, showsIndicators: false) {
            VStack (){
                Text("Ross's ID")
                    .font(.title3)
                    .frame(width: 325, height: 20, alignment: .topLeading)
                    .bold()
                Text("Front Door")
                    .frame(width: 325, height: 70, alignment: .topLeading)
                Button(action: {
                    authenticate()
                }) {
                    Text("Activate Card")
                        .foregroundColor(Color.white)
                }
                .frame(width: 175, height: 40)
                .background(Color.blue)
                .cornerRadius(10)
            }
            .border(3, Color.black)
            .background() {
                LinearGradient(
                    colors: [Color.gray, Color.blue],
                    startPoint: .topLeading, endPoint: .bottomTrailing)
                .edgesIgnoringSafeArea(.all)
                .hueRotation(.degrees(animateGradient ? 40 : 0))
                .onAppear {
                    withAnimation(.easeInOut(duration: 6).repeatForever(autoreverses: true)) {
                        animateGradient.toggle()
                    }
                }
                .opacity(0.5)
            }
            
            VStack (){
                Text("Invalid ID")
                    .font(.title3)
                    .frame(width: 325, height: 20, alignment: .topLeading)
                    .bold()
                Text("Wrong Door")
                    .frame(width: 325, height: 70, alignment: .topLeading)
                Button(action: {
                    authenticate2()
                }) {
                    Text("Activate Card")
                        .foregroundColor(Color.white)
                }
                .frame(width: 175, height: 40)
                .background(Color.blue)
                .cornerRadius(10)
            }
            .border(3, Color.black)
            .background() {
                LinearGradient(
                    colors: [Color.gray, Color.blue],
                    startPoint: .topLeading, endPoint: .bottomTrailing)
                .edgesIgnoringSafeArea(.all)
                .hueRotation(.degrees(animateGradient ? 40 : 0))
                .onAppear {
                    withAnimation(.easeInOut(duration: 6).repeatForever(autoreverses: true)) {
                        animateGradient.toggle()
                    }
                }
                .opacity(0.5)
            }
            
            VStack (){
                Text("Sean's ID")
                    .font(.title3)
                    .frame(width: 325, height: 20, alignment: .topLeading)
                    .bold()
                Text("Front Door")
                    .frame(width: 325, height: 70, alignment: .topLeading)
                Button(action: {
                    authenticate3()
                }) {
                    Text("Activate Card")
                        .foregroundColor(Color.white)
                }
                .frame(width: 175, height: 40)
                .background(Color.blue)
                .cornerRadius(10)
            }
            .border(3, Color.black)
            .background() {
                LinearGradient(
                    colors: [Color.gray, Color.blue],
                    startPoint: .topLeading, endPoint: .bottomTrailing)
                .edgesIgnoringSafeArea(.all)
                .hueRotation(.degrees(animateGradient ? 40 : 0))
                .onAppear {
                    withAnimation(.easeInOut(duration: 6).repeatForever(autoreverses: true)) {
                        animateGradient.toggle()
                    }
                }
                .opacity(0.5)
            }
            .navigationTitle("Digital Cards")
        }
        .refreshable{}
    }
    
    func authenticate() {
        let context = LAContext()
        var error: NSError?
        
        if
            context.canEvaluatePolicy( .deviceOwnerAuthenticationWithBiometrics, error: &error) {
            context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: "To authenticate user to use ID") {
                success, authenticationError in
                
                if success {
                    writer.scanner(thedata: ID1)
                }
                else {
                    text = "ERROR: Unable to authenticate user"
                }
            }
        }
    }
    
    func authenticate2() {
        let context = LAContext()
        var error: NSError?
        
        if
            context.canEvaluatePolicy( .deviceOwnerAuthenticationWithBiometrics, error: &error) {
            context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: "To authenticate user to use ID") {
                success, authenticationError in
                
                if success {
                    writer.scanner(thedata: ID2)
                }
                else {
                    text = "ERROR: Unable to authenticate user"
                }
            }
        }
    }
    
    func authenticate3() {
        let context = LAContext()
        var error: NSError?
        
        if
            context.canEvaluatePolicy( .deviceOwnerAuthenticationWithBiometrics, error: &error) {
            context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: "To authenticate user to use ID") {
                success, authenticationError in
                
                if success {
                    writer.scanner(thedata: ID3)
                }
                else {
                    text = "ERROR: Unable to authenticate user"
                }
            }
        }
    }
}

struct CardView_Previews: PreviewProvider {
    static var previews: some View {
        CardView()
    }
}

class NFCReader: NSObject, ObservableObject, NFCNDEFReaderSessionDelegate {
    var realData = ""
    var nfcSession: NFCNDEFReaderSession?
    
    func scanner(thedata: String) {
        realData = thedata
        nfcSession = NFCNDEFReaderSession(delegate: self, queue: nil, invalidateAfterFirstRead: true)
        nfcSession?.alertMessage = "Hold Near Reader"
        nfcSession?.begin()
    }
    
    func readerSession(_ session: NFCNDEFReaderSession, didInvalidateWithError error: Error) {
        
    }
    
    func readerSession(_ session: NFCNDEFReaderSession, didDetectNDEFs messages: [NFCNDEFMessage]) {
        
    }
    
    func readerSession(_ session: NFCNDEFReaderSession, didDetect tags: [NFCNDEFTag]) {
        let str:String = realData
        if tags.count > 1{
            let retry = DispatchTimeInterval.milliseconds(500)
            session.alertMessage = "ERROR: More than one Tag detected"
            DispatchQueue.global().asyncAfter(deadline: .now() + retry, execute: {session.restartPolling()})
            return
        }
        
        let tag = tags.first!
        session.connect(to: tag, completionHandler: {(error: Error?) in if nil != error {
            session.alertMessage = "ERROR: Unable to connect to Reader"
            session.invalidate()
            return
        }
            tag.queryNDEFStatus(completionHandler: {(ndefstatus: NFCNDEFStatus, capacity: Int, error: Error?)
                in guard error == nil else {
                    session.alertMessage = "ERROR: Unable to query NDEF Status"
                    session.invalidate()
                    return
                }
                switch ndefstatus {
                case .notSupported:
                    session.alertMessage = "ERROR: This reader is not supported by the phone"
                    session.invalidate()
                
                case .readOnly:
                    session.alertMessage = "ERROR: Tag is in read-only mode"
                    session.invalidate()
                
                case .readWrite:
                    tag.writeNDEF(.init(records: [NFCNDEFPayload.wellKnownTypeURIPayload(string: "\(str)")!]), completionHandler: {(error: Error?) in
                        if nil != error {
                            session.alertMessage = "ERROR: Write NDEF Message Failed"
                        } else {
                            session.alertMessage = "NFC Reader Found"
                        }
                        session.invalidate()
                    })
                @unknown default:
                    session.alertMessage = "ERROR: Unknown Error"
                    session.invalidate()
                }
            })
        })
    }
}
