from flask import Flask, jsonify, render_template
import time
import ctypes
import threading

app = Flask(__name__)


class WebsiteTimeTracker:
    def __init__(self):
        self.start_time = None
        self.current_website = None
        self.website_data = {}
        self.tracking = False

    def get_active_window_title(self):
        try:
            foreground_window = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(foreground_window)
            buff = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(foreground_window, buff, length + 1)
            return buff.value
        except Exception as e:
            print(f"Error getting active window title: {e}")
            return None

    def track_website_time(self, website):
        current_time = time.time()

        if self.current_website != website:

            if self.current_website:
                elapsed_time = current_time - self.start_time
                self.website_data[self.current_website] = self.website_data.get(self.current_website, 0) + elapsed_time


            self.current_website = website
            self.start_time = current_time

    def start_tracking(self):
        self.tracking = True
        self.website_data = {}
        while self.tracking:
            active_window = self.get_active_window_title()
            if active_window:
                self.track_website_time(active_window)
            time.sleep(0.1)

    def stop_tracking(self):
        self.tracking = False

        if self.current_website:
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            self.website_data[self.current_website] = self.website_data.get(self.current_website, 0) + elapsed_time


        result = {}
        for website, cumulative_time in self.website_data.items():
            result[website] = round(cumulative_time, 2)
        return result


tracker = WebsiteTimeTracker()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start_tracking", methods=["POST"])
def start_tracking():
    global tracker
    if not tracker.tracking:
        tracker = WebsiteTimeTracker()
        tracking_thread = threading.Thread(target=tracker.start_tracking)
        tracking_thread.start()
        return jsonify({"status": "success", "message": "Tracking started!"})
    else:
        return jsonify({"status": "error", "message": "Tracking is already started!"})


@app.route("/stop_tracking", methods=["POST"])
def stop_tracking():
    global tracker
    if tracker.tracking:
        result = tracker.stop_tracking()
        return jsonify(result)
    else:
        return jsonify({"status": "error", "message": "Tracking is not started!"})


if __name__ == "__main__":
    app.run(debug=True)

