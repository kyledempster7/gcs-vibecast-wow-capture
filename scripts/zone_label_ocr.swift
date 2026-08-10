// zone_label_ocr.swift — macOS Vision OCR on one image path. stdout = plain text lines.
// Usage: swift zone_label_ocr.swift /path/to/frame.jpg
import Foundation
import Vision
import AppKit

guard CommandLine.arguments.count >= 2 else {
    fputs("usage: zone_label_ocr.swift <image>\n", stderr)
    exit(2)
}
let path = CommandLine.arguments[1]
guard let img = NSImage(contentsOfFile: path),
      let tiff = img.tiffRepresentation,
      let rep = NSBitmapImageRep(data: tiff),
      let cg = rep.cgImage else {
    fputs("load_fail\n", stderr)
    exit(3)
}

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = true
let handler = VNImageRequestHandler(cgImage: cg, options: [:])
do {
    try handler.perform([request])
} catch {
    fputs("vision_fail \(error)\n", stderr)
    exit(4)
}
let observations = request.results ?? []
for o in observations {
    if let s = o.topCandidates(1).first?.string {
        print(s)
    }
}
