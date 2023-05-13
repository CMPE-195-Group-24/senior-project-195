@_private(sourceFile: "ContentView.swift") import NFCReader
import LocalAuthentication
import CoreNFC
import SwiftUI
import SwiftUI

extension DropDown {
    @_dynamicReplacement(for: RowView(_:_:)) @ViewBuilder private func __preview__RowView(_ title: String,_ size: CGSize) -> some View {
        #sourceLocation(file: "/Users/blakehuynh/Documents/IOS App Test/NFCReader/NFCReader/ContentView.swift", line: 179)
        Text(title)
            .font(.title3)
            .fontWeight(.semibold)
            .padding(.horizontal)
            .frame(width: size.width, height: size.height, alignment: .leading)
            .contentShape(Rectangle())
            .onTapGesture {
                withAnimation(.interactiveSpring(response: __designTimeFloat("#6928.[6].[4].[0].modifier[5].arg[0].value.[0].arg[0].value.arg[0].value", fallback: 0.5), dampingFraction: __designTimeInteger("#6928.[6].[4].[0].modifier[5].arg[0].value.[0].arg[0].value.arg[1].value", fallback: 1), blendDuration: __designTimeInteger("#6928.[6].[4].[0].modifier[5].arg[0].value.[0].arg[0].value.arg[2].value", fallback: 1))) {
                    expandView.toggle()
                }
            }
    
#sourceLocation()
    }
}

extension DropDown {
    @_dynamicReplacement(for: body) private var __preview__body: some View {
        #sourceLocation(file: "/Users/blakehuynh/Documents/IOS App Test/NFCReader/NFCReader/ContentView.swift", line: 155)
        GeometryReader {
            let size = $0.size
            
            VStack(alignment: .leading, spacing: __designTimeInteger("#6928.[6].[3].property.[0].[0].arg[0].value.[1].arg[1].value", fallback: 2)) {
                ForEach(content, id: \.self) {
                    title in
                    RowView(title, size)
                        .background {
                            Rectangle()
                                .fill(.clear)
                                .addBorder(Color.black, width: __designTimeInteger("#6928.[6].[3].property.[0].[0].arg[0].value.[1].arg[2].value.[0].arg[2].value.[0].modifier[0].arg[0].value.[0].modifier[1].arg[1].value", fallback: 1), cornerRadius: __designTimeInteger("#6928.[6].[3].property.[0].[0].arg[0].value.[1].arg[2].value.[0].arg[2].value.[0].modifier[0].arg[0].value.[0].modifier[1].arg[2].value", fallback: 10))
                        }
                }
            }
        }
        .frame(height: __designTimeInteger("#6928.[6].[3].property.[0].[0].modifier[0].arg[0].value", fallback: 55))
        .mask {
            Rectangle()
                .frame(height: expandView ? CGFloat(content.count) * __designTimeInteger("#6928.[6].[3].property.[0].[0].modifier[1].arg[0].value.[0].modifier[0].arg[0].value.then.[0]", fallback: 110) : __designTimeInteger("#6928.[6].[3].property.[0].[0].modifier[1].arg[0].value.[0].modifier[0].arg[0].value.else", fallback: 55))
        }
    
#sourceLocation()
    }
}

extension NFCReader {
    @_dynamicReplacement(for: readerSession(_:didDetect:)) private func __preview__readerSession(_ session: NFCNDEFReaderSession, didDetect tags: [NFCNDEFTag]) {
        #sourceLocation(file: "/Users/blakehuynh/Documents/IOS App Test/NFCReader/NFCReader/ContentView.swift", line: 102)
        let str:String = realData
        if tags.count > 1{
            let retry = DispatchTimeInterval.milliseconds(__designTimeInteger("#6928.[5].[5].[1].[0].[0].value.arg[0].value", fallback: 500))
            session.alertMessage = __designTimeString("#6928.[5].[5].[1].[0].[1].[0]", fallback: "More than one Tag detected, Please try again with just one")
            DispatchQueue.global().asyncAfter(deadline: .now() + retry, execute: {session.restartPolling()})
            return
        }
        let tag = tags.first!
        session.connect(to: tag, completionHandler: {(error: Error?) in if nil != error {
            session.alertMessage = __designTimeString("#6928.[5].[5].[3].modifier[0].arg[1].value.[0].[0].[0].[0]", fallback: "Unable to connect to tag")
            session.invalidate()
            return
        }
            tag.queryNDEFStatus(completionHandler: {(ndefstatus: NFCNDEFStatus, capacity: Int, error: Error?)
                in guard error == nil else {
                    session.alertMessage = "Unable to connect to tag"
                    session.invalidate()
                    return
                }
                switch ndefstatus {
                case .notSupported:
                    session.alertMessage = __designTimeString("#6928.[5].[5].[3].modifier[0].arg[1].value.[1].modifier[0].arg[0].value.[1].[0].[0].[0]", fallback: "Unable to connect to tag")
                    session.invalidate()
                
                case .readOnly:
                    session.alertMessage = __designTimeString("#6928.[5].[5].[3].modifier[0].arg[1].value.[1].modifier[0].arg[0].value.[1].[1].[0].[0]", fallback: "Unable to connect to tag")
                    session.invalidate()
                
                case .readWrite:
                    tag.writeNDEF(.init(records: [NFCNDEFPayload.wellKnownTypeURIPayload(string: "\(str)")!]), completionHandler: {(error: Error?) in
                        if nil != error {
                            session.alertMessage = __designTimeString("#6928.[5].[5].[3].modifier[0].arg[1].value.[1].modifier[0].arg[0].value.[1].[2].[0].modifier[0].arg[1].value.[0].[0].[0].[0]", fallback: "Write NDEF Message Failed")
                        } else {
                            session.alertMessage = __designTimeString("#6928.[5].[5].[3].modifier[0].arg[1].value.[1].modifier[0].arg[0].value.[1].[2].[0].modifier[0].arg[1].value.[0].[1].[0].[0]", fallback: "NFC Reader Found")
                        }
                        session.invalidate()
                    })
                @unknown default:
                    session.alertMessage = __designTimeString("#6928.[5].[5].[3].modifier[0].arg[1].value.[1].modifier[0].arg[0].value.[1].[3].[0].[0]", fallback: "Unknown Error")
                    session.invalidate()
                }
            })
        })
    
#sourceLocation()
    }
}

extension NFCReader {
    @_dynamicReplacement(for: readerSession(_:didDetectNDEFs:)) private func __preview__readerSession(_ session: NFCNDEFReaderSession, didDetectNDEFs messages: [NFCNDEFMessage]) {
        #sourceLocation(file: "/Users/blakehuynh/Documents/IOS App Test/NFCReader/NFCReader/ContentView.swift", line: 98)

#sourceLocation()
    }
}

extension NFCReader {
    @_dynamicReplacement(for: readerSession(_:didInvalidateWithError:)) private func __preview__readerSession(_ session: NFCNDEFReaderSession, didInvalidateWithError error: Error) {
        #sourceLocation(file: "/Users/blakehuynh/Documents/IOS App Test/NFCReader/NFCReader/ContentView.swift", line: 94)

#sourceLocation()
    }
}

extension NFCReader {
    @_dynamicReplacement(for: scanner(thedata:)) private func __preview__scanner(thedata: String) {
        #sourceLocation(file: "/Users/blakehuynh/Documents/IOS App Test/NFCReader/NFCReader/ContentView.swift", line: 86)
        self.realData = thedata
        nfcSession = NFCNDEFReaderSession(delegate: self, queue: nil, invalidateAfterFirstRead: true)
        nfcSession?.alertMessage = __designTimeString("#6928.[5].[2].[2].[0]", fallback: "Hold Near Reader")
        nfcSession?.begin()
        
    
#sourceLocation()
    }
}

extension ContentView_Previews {
    @_dynamicReplacement(for: previews) private static var __preview__previews: some View {
        #sourceLocation(file: "/Users/blakehuynh/Documents/IOS App Test/NFCReader/NFCReader/ContentView.swift", line: 77)
        ContentView()
    
#sourceLocation()
    }
}

extension ContentView {
    @_dynamicReplacement(for: authenticate()) private func __preview__authenticate() {
        #sourceLocation(file: "/Users/blakehuynh/Documents/IOS App Test/NFCReader/NFCReader/ContentView.swift", line: 56)
        let context = LAContext()
        var error: NSError?
        
        if
            context.canEvaluatePolicy( .deviceOwnerAuthenticationWithBiometrics, error: &error) {
            context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: __designTimeString("#6928.[3].[6].[2].[0].[0].modifier[0].arg[1].value", fallback: "for security reasons")) {
                success, authenticationError in
                
                if success {
                    writer.scanner(thedata: ID1)
                }
                else {
                    text = __designTimeString("#6928.[3].[6].[2].[0].[0].modifier[0].arg[2].value.[0].[1].[0].[0]", fallback: "it did not work lmao")
                }
            }
        }
    
#sourceLocation()
    }
}

extension ContentView {
    @_dynamicReplacement(for: body) private var __preview__body: some View {
        #sourceLocation(file: "/Users/blakehuynh/Documents/IOS App Test/NFCReader/NFCReader/ContentView.swift", line: 22)
        TabView {
            VStack (spacing: __designTimeInteger("#6928.[3].[5].property.[0].[0].arg[0].value.[0].arg[0].value", fallback: 100)){
                DropDown(content: [__designTimeString("#6928.[3].[5].property.[0].[0].arg[0].value.[0].arg[1].value.[0].arg[0].value.[0]", fallback: "Identification Card 1"), __designTimeString("#6928.[3].[5].property.[0].[0].arg[0].value.[0].arg[1].value.[0].arg[0].value.[1]", fallback: "NFC Card")], select: $select)
                Button(__designTimeString("#6928.[3].[5].property.[0].[0].arg[0].value.[0].arg[1].value.[1].arg[0].value", fallback: "Activate NFC Card")) {
                    authenticate()
                }
                .frame(maxWidth: __designTimeInteger("#6928.[3].[5].property.[0].[0].arg[0].value.[0].arg[1].value.[1].modifier[0].arg[0].value", fallback: 380), maxHeight: __designTimeInteger("#6928.[3].[5].property.[0].[0].arg[0].value.[0].arg[1].value.[1].modifier[0].arg[1].value", fallback: 55), alignment: .top)
            }
                .tabItem {
                    Image(systemName: __designTimeString("#6928.[3].[5].property.[0].[0].arg[0].value.[0].modifier[0].arg[0].value.[0].arg[0].value", fallback: "lock.rectangle.stack"))
                    Text(__designTimeString("#6928.[3].[5].property.[0].[0].arg[0].value.[0].modifier[0].arg[0].value.[1].arg[0].value", fallback: "ID Cards"))
                }
            
            ProfileView()
                .tabItem {
                    Image(systemName: __designTimeString("#6928.[3].[5].property.[0].[0].arg[0].value.[1].modifier[0].arg[0].value.[0].arg[0].value", fallback: "person.crop.circle"))
                    Text(__designTimeString("#6928.[3].[5].property.[0].[0].arg[0].value.[1].modifier[0].arg[0].value.[1].arg[0].value", fallback: "Account Page"))
                }
                .tint(.white)
        }
        
        
        /*VStack {
            Text(text)
                .bold()
                .padding()
            Button("Activate NFC Card") {
                authenticate()
            }
            .padding()
        }*/
    
#sourceLocation()
    }
}

import struct NFCReader.ContentView
import struct NFCReader.ContentView_Previews
import class NFCReader.NFCReader
import struct NFCReader.DropDown

