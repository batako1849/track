import cv2


def myfunc(i):
    pass # do nothing
    

cv2.namedWindow('MotionDetected Frame') # create win with win name
cv2.namedWindow('MotionDetected Area Frame') # create win with win name

cv2.createTrackbar('α*10', # name of value
                   'MotionDetected Area Frame', # win name
                   0, # min
                   10, # max
                   myfunc) # callback func

cap = cv2.VideoCapture(0)

ok = False
before = None
detected_frame = None
bbox = (0,0,0,0)
while True:
    #  OpenCVでWebカメラの画像を取り込む
    ret, frame = cap.read()
    
    v1 = cv2.getTrackbarPos('α*10',  # get the value
                           'MotionDetected Area Frame')  # of the win

    # 取り込んだフレームに対して差分をとって動いているところが明るい画像を作る
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if before is None:
        before = gray.copy().astype('float')
        continue
    #現在のフレームと移動平均との間の差を計算する.
    v1 = v1/10
    cv2.accumulateWeighted(gray, before, v1)
    mdframe = cv2.absdiff(gray, cv2.convertScaleAbs(before))
    # 動く部分を白で表示する.
    cv2.imshow('MotionDetected Frame', mdframe)

    # 動いているエリアの面積を計算してちょうどいい検知結果を抽出する
    thresh = cv2.threshold(mdframe, 3, 255, cv2.THRESH_BINARY)[1]
    # 輪郭抽出
    image, contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_area = 0
    target = None
    for cnt in contours:
        #領域の面積
        area = cv2.contourArea(cnt)
        if max_area < area and area < 40000 and area > 4000:
            max_area = area;
            target = cnt

    # 動いているエリアのうちそこそこの大きさのものがあればそれを矩形で表示する
    # ちょうどいいエリアがなかったら最後の動いているエリアがあるフレームとエリア情報を用いてトラッキングをする
    # 動体が検出されない時その旨を表示する.
    if max_area <= 4000:
        track = False
        if detected_frame is not None:
            tracker = cv2.TrackerKCF_create()
            #tracker = cv2.TrackerMIL_create()
            #tracker = cv2.TrackerBOOSTING_create()
            #tracker = cv2.TrackerMEDIANFLOW_create()
            #tracker = cv2.TrackerTLD_create()
            ok = tracker.init(detected_frame, bbox)
            detected_frame = None

        if ok:
            track, bbox = tracker.update(frame)
        if track:
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(frame, p1, p2, (0,255,0), 2, 1)          
            cv2.putText(frame, "tracking", (10,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)
        else:
            ok = False
            cv2.putText(frame, "No things detected", (10,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)
    elif max_area > 4000 and max_area <= 6000:

        x,y,w,h = cv2.boundingRect(target)
        bbox = (x,y,w,h)
        detected_frame = frame.copy()
        frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        cv2.putText(frame, "motion detected", (10,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)
    else:
        (x,y),radius = cv2.minEnclosingCircle(target)
        center = (int(x),int(y))
        radius = int(radius)
        frame = cv2.circle(frame,center,radius,(0,255,0),2)
        cv2.putText(frame, "motion detected", (10,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)
    cv2.imshow('MotionDetected Area Frame', frame)
    # キー入力を1ms待って、k が27（ESC）だったらBreakする
    k = cv2.waitKey(1)
    if k == 27:
        break

# キャプチャをリリースして、ウィンドウをすべて閉じる
cap.release()
cv2.destroyAllWindows()