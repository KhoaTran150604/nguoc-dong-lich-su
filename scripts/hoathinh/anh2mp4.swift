// Ghép chuỗi ảnh JPG/PNG thành MP4 H.264 bằng AVFoundation (không cần ffmpeg).
// Dùng: swift anh2mp4.swift <thư mục ảnh> <fps> <out.mp4>
import AVFoundation
import CoreGraphics
import Foundation
import ImageIO

let a = CommandLine.arguments
guard a.count >= 4 else { print("swift anh2mp4.swift <dir> <fps> <out.mp4>"); exit(1) }
let dir = URL(fileURLWithPath: a[1])
let fps = Int32(a[2])!
let out = URL(fileURLWithPath: a[3])
let files = try! FileManager.default.contentsOfDirectory(atPath: dir.path)
    .filter { $0.hasSuffix(".jpg") || $0.hasSuffix(".png") }.sorted()
guard let first = files.first else { print("không có ảnh"); exit(1) }

func load(_ name: String) -> CGImage {
    let src = CGImageSourceCreateWithURL(dir.appendingPathComponent(name) as CFURL, nil)!
    return CGImageSourceCreateImageAtIndex(src, 0, nil)!
}
let img0 = load(first)
let w = img0.width, h = img0.height
try? FileManager.default.removeItem(at: out)
let writer = try! AVAssetWriter(outputURL: out, fileType: .mp4)
let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
    AVVideoCodecKey: AVVideoCodecType.h264,
    AVVideoWidthKey: w, AVVideoHeightKey: h,
    AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 16_000_000,
                                      AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel],
])
input.expectsMediaDataInRealTime = false
let ad = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [
    kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB,
    kCVPixelBufferWidthKey as String: w, kCVPixelBufferHeightKey as String: h,
])
writer.add(input)
writer.startWriting()
writer.startSession(atSourceTime: .zero)
for (i, f) in files.enumerated() {
    let img = i == 0 ? img0 : load(f)
    while !input.isReadyForMoreMediaData { usleep(2000) }
    var pb: CVPixelBuffer?
    CVPixelBufferPoolCreatePixelBuffer(nil, ad.pixelBufferPool!, &pb)
    CVPixelBufferLockBaseAddress(pb!, [])
    let ctx = CGContext(data: CVPixelBufferGetBaseAddress(pb!), width: w, height: h, bitsPerComponent: 8,
                        bytesPerRow: CVPixelBufferGetBytesPerRow(pb!), space: CGColorSpaceCreateDeviceRGB(),
                        bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue)!
    ctx.draw(img, in: CGRect(x: 0, y: 0, width: w, height: h))
    CVPixelBufferUnlockBaseAddress(pb!, [])
    ad.append(pb!, withPresentationTime: CMTime(value: CMTimeValue(i), timescale: fps))
}
input.markAsFinished()
let sem = DispatchSemaphore(value: 0)
writer.finishWriting { sem.signal() }
sem.wait()
print("xong: \(out.path) (\(files.count) khung, \(w)x\(h))")
