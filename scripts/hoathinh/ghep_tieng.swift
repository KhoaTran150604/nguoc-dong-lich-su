// Ghép tiếng (wav/mp3/m4a) vào video MP4 bằng AVFoundation (máy không có ffmpeg).
// Dùng: swift ghep_tieng.swift <video.mp4> <audio> <out.mp4>
import AVFoundation
import Foundation

let a = CommandLine.arguments
guard a.count >= 4 else { print("swift ghep_tieng.swift <video.mp4> <audio> <out.mp4>"); exit(1) }
let video = AVURLAsset(url: URL(fileURLWithPath: a[1]))
let audio = AVURLAsset(url: URL(fileURLWithPath: a[2]))
let out = URL(fileURLWithPath: a[3])
try? FileManager.default.removeItem(at: out)

let comp = AVMutableComposition()
let sem = DispatchSemaphore(value: 0)
Task {
    do {
        let vt = try await video.loadTracks(withMediaType: .video).first!
        let at = try await audio.loadTracks(withMediaType: .audio).first!
        let vdur = try await video.load(.duration)
        let adur = try await audio.load(.duration)
        let cv = comp.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid)!
        try cv.insertTimeRange(CMTimeRange(start: .zero, duration: vdur), of: vt, at: .zero)
        let ca = comp.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid)!
        try ca.insertTimeRange(CMTimeRange(start: .zero, duration: CMTimeMinimum(vdur, adur)), of: at, at: .zero)
        let ex = AVAssetExportSession(asset: comp, presetName: AVAssetExportPresetPassthrough)!
        ex.outputURL = out
        ex.outputFileType = .mp4
        await ex.export()
        if ex.status != .completed { print("lỗi:", ex.error ?? "?") ; exit(1) }
        print("xong: \(out.path)")
    } catch { print("lỗi:", error); exit(1) }
    sem.signal()
}
sem.wait()
