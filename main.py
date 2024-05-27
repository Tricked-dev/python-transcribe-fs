# whisperx iceberg.mp3 --device cpu --diarize --compute_type 'int8' --hf_token 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 --threads --output_dir ./out --output_format vtt
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import webvtt


INPUT = "./input"
OUTPUT = "./out"


class MyHandler(FileSystemEventHandler):
    jobs = {}
    sizes = {}

    def start_job(self, path):
        print(f"Starting job for {path}")

        # fmt: off
        command = [
            "whisperx",
            path,
            "--device", "cpu",
            "--diarize",
            "--compute_type", "int8",
            "--hf_token", "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",
            "--threads", "12",
            "--output_dir", OUTPUT,
            "--output_format", "vtt"
        ]
        # fmt: on
        print(" ".join(command))
        process = subprocess.Popen(
            command,
        )
        self.jobs[path] = process

    def run_job(self, path):
        size = os.path.getsize(path)
        if self.jobs.get(path):
            if self.jobs[path].poll() is not None:
                print(f"Job for {path} has finished")
            else:
                if size == self.sizes.get(path):
                    print(
                        f"Skipping job for {path} because the file size hasn't changed"
                    )
                    return
                self.jobs[path].kill()
                print(f"Killed job for {path}")
            del self.jobs[path]
        self.sizes[path] = size
        self.start_job(path)

    def on_modified(self, event):
        if event.is_directory:
            return
        self.run_job(event.src_path)

    def on_created(self, event):
        if event.is_directory:
            return
        self.run_job(event.src_path)

    def on_deleted(self, event):
        if self.jobs.get(event.src_path):
            self.jobs[event.src_path].kill()
            del self.jobs[event.src_path]


class VttToTxtHandler(FileSystemEventHandler):
    cooking = False

    def on_modified(self, event):
        if self.cooking:
            return
        self.cooking = True
        try:
            for filename in os.listdir(OUTPUT):
                if filename.endswith(".vtt"):
                    path = os.path.join(OUTPUT, filename)
                    print(f"Converting {filename} to txt")
                    res = []
                    for caption in webvtt.read(path):
                        res.append(
                            caption.text.replace("[", "\n")
                            .replace("]", "")
                            .replace(": ", ":\n")
                            .replace("SPEAKER_", "Person ")
                            .replace("00", "1")
                            .replace("01", "2")
                            .replace("0", "")
                        )

                    with open(path.replace(".vtt", ".txt"), "w") as f:
                        f.write("\n".join(res))
                    print(f"Converted {path} to txt")
                    os.remove(path)
        finally:
            self.cooking = False


if __name__ == "__main__":
    handler = MyHandler()
    observer = Observer()
    observer.schedule(handler, path=INPUT, recursive=True)
    vttHandler = VttToTxtHandler()
    observer.schedule(vttHandler, path=OUTPUT, recursive=True)
    observer.start()
    observer.join()
