# OpenCVをインポート
import cv2
import json

file_name = 'tukaremaru-avatar'
# サンプル動画ファイル
videoPath = "{}.webm".format(file_name)


def buildVideoCaptures(videoPath, candidates):
    cap = cv2.VideoCapture(videoPath)
    # 1000
    default_frame_rate = cap.get(cv2.CAP_PROP_FPS)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        return

    # フレーム数を取得
    # TODO ここが負になるのも意味不明
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    # time_end = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)

    for i, candidate in enumerate(candidates):
        candidate_unit = 10000000
        time_location = (candidate["offset"] + candidate["duration"]) / candidate_unit
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        frame_location = time_location * frame_rate
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_location)
        # TODO ここがなぜかNoneで帰ってくるのは?
        _, img = cap.read()
        # imgは読み込んだフレームのNumpy配列でのピクセル情報(BGR)
        # imgのshapeは (高さ, 横幅, 3)

        # 画像サイズを取得
        width = img.shape[1]
        height = img.shape[0]

        # 縮小後のサイズを決定
        newWidth = width
        newHeight = int(height * newWidth / width)

        # リサイズ
        img = cv2.resize(img, (newWidth, newHeight))

        # 画像ファイルで書き出す
        # ファイル名には連番を付ける
        outputPath = "{}-thumbnail-{}.png".format(file_name, i)
        cv2.imwrite(outputPath, img)
    print('thumbnail got')


candidatesPath = 'transcription_{}.json'.format(file_name)
candidates = []
with open(candidatesPath) as f:
    text = f.read()
    candidates = json.loads(text)
buildVideoCaptures(videoPath, candidates)
