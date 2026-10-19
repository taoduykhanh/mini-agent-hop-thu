# Spec: Bot MU Lục Địa VNG trên LDPlayer — quá trình, khó khăn và câu hỏi cần hỗ trợ

## Mục đích tài liệu

Tóm tắt toàn bộ quá trình reverse-engineering và xây dựng bot cho game MU Lục Địa VNG (chạy trên giả lập LDPlayer), gồm những gì đã làm được, những đường đã thử và có kết luận chắc chắn, và những khó khăn còn mở — để trao đổi với Claude Code xem có hướng giải quyết nào tốt hơn không.

Người dùng học reverse-engineering bằng cách tự làm: mỗi thí nghiệm phải đi đến kết luận rõ ràng, kể cả khi kết quả là "không làm được", và kết luận âm tính đó vẫn là một kết quả có giá trị.

## Mục tiêu cuối cùng

Xây dựng bot ngang tầm các tool thương mại (SmartPK, 360Auto), cụ thể là:

- Đọc trạng thái game từ RAM (HP nhân vật, tọa độ, sau này là danh sách thực thể/boss)
- Tự hồi sinh khi chết
- Biết boss nào còn sống, boss nào sắp hồi sinh, tự di chuyển đến đánh
- Ghi và di chuyển đến tọa độ đã lưu, giống chức năng "Ghi Tọa độ hiện tại" của SmartPK
- Không dừng ở mức auto-click/macro mù như tính năng tích hợp sẵn của LDPlayer — bot phải đọc state rồi mới ra quyết định

## Môi trường và kiến trúc đã chốt

- Game: MU Lục Địa VNG, Unity IL2CPP, logic C# đã obfuscate, có khả năng một phần logic nằm trong các bundle xLua (`lua.u3d.v395` — chưa đào sâu)
- Giả lập: LDPlayer (tiến trình host là `Ld9BoxHeadless.exe`), đã bật root trong guest Android
- Tap/thao tác: `adb -s emulator-5554` trực tiếp, screenshot bằng `adb screencap` (không dùng `ldconsole`)
- Hướng đọc RAM đã chốt: **đọc từ phía host (Windows) bằng `ReadProcessMemory` (ctypes, Python)** vào tiến trình `Ld9BoxHeadless.exe`
- Hướng đọc trong-guest (qua `/proc/<pid>/mem` bằng root) đã thử và bỏ — xem mục kết luận âm tính bên dưới

## Bài học từ việc mổ xẻ 2 tool thương mại

### SmartPK (APK Android, `app.smartpk.mu` v1.0.6)

- Bản chất là loader, không có native `.so` trong APK: lúc chạy mới tải AppConfig từ `service-mu.smartpk.app:9006` và ResourceConfig khớp phiên bản game, có kiểm tra MD5 — đây là lý do tool phải bán theo thuê bao
- Yêu cầu root: đọc/ghi bộ nhớ game qua `su`, inject tap vào `/dev/input` (không dùng Accessibility Service), đọc dữ liệu game qua `Android/data/vng.games.mu.webzen.online`
- Giữ sống bằng foreground service + WakeLock + BootReceiver + Watchdog + overlay
- Logic lõi bị obfuscate và tải về lúc chạy, không nằm sẵn trong APK

### 360Auto (Windows, bản 2.1.0.3, MOBOT TECHNOLOGY JSC)

- Có 2 tầng. Tầng điều khiển là WebSocket bền vững tới `wss://remote.360auto.net/ws/desktop?role=portal&machine=..&uid=..` với các lệnh kiểu `_hello/_idle/launch <product_id>/stop/restart/host_sub` — server là "não", PC chỉ là cổng thực thi
- Tầng thực thi là inject code vào tiến trình giả lập từ Windows (`OpenProcess`/`VirtualAllocEx`/`WriteProcessMemory`/`CreateRemoteThread` + thread hijack trong `360AutoExt.dll`), đọc/ghi RAM guest từ bên ngoài VM nên teleport được tức thì; không hề dùng `ldconsole`/`adb`, không cần root hay Debug ADB trong Android
- Screenshot qua DXGI Desktop Duplication
- Mô hình kinh doanh: mã VIP theo thuê bao + kho "product" theo từng game, tải về lúc chạy — giống SmartPK

Kết luận rút ra: các tool thương mại đều phải ship offsets theo từng phiên bản game từ server, vì không có cách ổn định để tự suy ra địa chỉ mỗi phiên chạy. Bot tự làm phải chấp nhận đánh đổi này hoặc tìm được cơ chế quét tự động đủ nhanh.

## Những gì đã làm được (đã kiểm chứng chạy thật)

### 1. Tự hồi sinh dựa trên HP đọc từ RAM host

- Quét giá trị chính xác (exact-value scan kiểu Cheat Engine) tìm được địa chỉ HP trong `Ld9BoxHeadless.exe`; việc đọc thì đúng, nhưng ghi/đóng băng HP không có tác dụng vì server là bên quyết định (authoritative)
- `doc_hp.py` (ctypes `ReadProcessMemory`) phát hiện chết đúng, và vòng lặp `vong_lap_tu_hoi_sinh.py` đã chạy end-to-end: HP = 0 → chờ 5 giây → tap nút hồi sinh đã calibrate qua adb, tối đa 3 lần thử
- `quet_hp_host.py` tự tìm địa chỉ HP trong khoảng 1–2 phút và lưu vào `hp_addr.txt` (ví dụ một phiên tìm được host `0x12387BB20`); vòng lặp hồi sinh tự đọc file này, không cần truyền địa chỉ tay nữa

### 2. Tìm cặp tọa độ X, Y trong một lượt quét

- Tọa độ tile X/Y là số nguyên 4 byte, không phải float (đọc float cho ra 0.00 — sai kiểu dữ liệu)
- Giả thuyết "X, Y nằm cạnh nhau trong bộ nhớ" đã được xác nhận: `tim_toa_do.py` chỉ cần nhập X và Y một lần, quét X rồi kiểm tra Y có nằm ở offset kề (±4 đến ±16 byte) không, không cần di chuyển nhân vật để lọc dần
- Ví dụ một phiên: 42 cặp ứng viên, cặp đúng là X=`0x107D35428`, Y=`0x107D35418`, đọc ra X=226, Y=66 khớp đúng số hiển thị trong game

### 3. Ghi tọa độ hiện tại kiểu SmartPK

- `ghi_toa_do.py`: đọc X, Y từ địa chỉ đã lưu trong `toa_do_addr.txt`, cho đặt tên điểm và ghi vào `waypoints.txt`; bản v2 lưu thêm tên map hiện tại cùng mỗi waypoint
- Mỗi lần ghi một điểm chỉ mất vài giây sau khi đã có địa chỉ

### 4. Hạ tầng tap và calibrate

- Công cụ calibrate vị trí nút dùng lại được (`calib_nut.py` v2: chụp screenshot sau đếm ngược 5 giây), thay cho việc đoán tọa độ từng tác vụ. Ví dụ đã calibrate: `nut_tui` [1865, 401], `nut_thu_hoi_1` [1682, 1005], `nut_thu_hoi_2` [1618, 977]
- Tool follow tài khoản phụ theo tài khoản chính (`mu-follow`): tap bằng adb trực tiếp vào từng cửa sổ giả lập mà không chiếm chuột Windows, nên nhiều tab tap độc lập cùng lúc được; v2 có map-jump follow — mất dấu leader quá X giây thì phát lại chuỗi tap "teleport tới leader" đã ghi, tối đa 3 lần

## Những đường đã thử và kết luận chắc chắn (âm tính)

### 1. Pointer chain phía host — bất khả thi về cấu trúc

Pointer scan chạy lại cho kết quả "Pointer paths: 0". RAM guest được map ẩn danh (anonymously mapped) và khác nhau sau mỗi lần khởi động giả lập, nên không tồn tại chuỗi pointer ổn định phía host để lần từ module base tới HP/X/Y. Đây là lý do SmartPK và 360Auto phải ship offsets theo phiên bản từ server.

Hệ quả: hiện tại mỗi phiên chơi vẫn phải chạy quét lại địa chỉ (HP khoảng 1–2 phút, tọa độ một lượt quét nữa). Người dùng đánh giá việc săn địa chỉ mỗi phiên có khi còn mệt hơn lợi ích bot mang lại — đây là nút thắt lớn nhất còn mở.

### 2. Quét HP trong-guest — không ra, đã bỏ

`quet_hp_guest.py` (v1 đến v4, có rút kinh nghiệm đóng băng tiến trình bằng SIGSTOP trước khi quét chậm vì HP là giá trị thay đổi liên tục) chạy khoảng 1,5 giờ mà cho 0 ứng viên: các lần đọc `/proc/<pid>/mem` không bao giờ chứa giá trị HP. Nguyên nhân chưa giải thích được. Hướng host-side là đường duy nhất đã chứng minh được.

### 3. Teleport bằng cách ghi tọa độ — thất bại chắc chắn

Đã ghi thử X+5 vào cả 3 ứng viên địa chỉ tile X: nhân vật không di chuyển. Hai khả năng còn lại: server quyết định vị trí (authoritative) nên ghi RAM không có tác dụng, hoặc vị trí thật là tọa độ world dạng float còn tile nguyên chỉ là giá trị hiển thị suy ra. Bot sẽ không có teleport tức thì kiểu 360Auto; di chuyển phải đi qua cơ chế của game (click bản đồ → nhân vật tự chạy).

### 4. Tìm HP theo tên field trong dump IL2CPP — không có

`Il2CppDumper` v6.7.46 chạy được trên `libil2cpp.so` + `global-metadata.dat` (metadata không mã hóa), nhưng không tìm thấy field nào mang tên HP do C# đã obfuscate. Mỏ neo cấu trúc duy nhất tìm được là `CSMainPlayerAction.Instance` với `mainPlayerTrans` ở offset `0x10` — phục vụ cho vị trí, không cho HP.

## Khó khăn còn mở

### 1. Di chuyển đến tọa độ chỉ định bằng bản đồ — chưa chính xác

Phương án hiện tại là `di_den_ban_do.py`: mở bản đồ thế giới, tính điểm tap từ tọa độ tile đích, tap, nhân vật tự chạy tới. Lần test đầu tiên cho 2 lỗi:

- Nhân vật đến **lệch vị trí** cần đến — chưa rõ công thức quy đổi từ tọa độ tile sang pixel trên bản đồ (điểm gốc, tỉ lệ, hay bản đồ có căn giữa nhân vật hay không)
- Việc đóng bản đồ bằng phím BACK làm bật popup hỏi đồng ý thoát game; đã chuyển sang nút đóng bản đồ calibrate riêng (`NUT_DONG_BAN_DO`) và chụp 3 ảnh debug (`debug_map_mo.png`, `debug_map_tap.png`, `debug_map_dong.png`) mỗi lần chạy, nhưng chưa có đủ dữ kiện ảnh bản đồ mở để sửa công thức theo hình học thật

### 2. Di chuyển bằng link chat — đã gác lại

Game có link tọa độ màu xanh dạng `[Tên bản đồ:X,Y]` (ví dụ `[Tên bản đồ:210,188]`) do nút Định Vị của game tạo ra; nhấn vào link là nhân vật chạy tới tọa độ đó, không cần mở bản đồ. Nhưng:

- Chưa kiểm chứng được việc tự gõ link trong chat có được game nhận thành link bấm được hay không, hay chỉ nút Định Vị mới tạo được link thật
- Game có 3 kênh (kênh 1, 2, 3): nhấn link có thể bị chuyển sang một kênh ngẫu nhiên

Phương án này đã bị gác lại để quay về đường bản đồ cho đơn giản.

### 3. Chưa đọc được trạng thái boss — khoảng cách lớn nhất với tool thương mại

SmartPK/360Auto biết boss nào còn sống, boss nào sắp hồi sinh để tự đến đánh, vì chúng đọc được danh sách thực thể (entity list) trong RAM. Bot hiện tại mới đọc được HP và tọa độ của chính nhân vật, chưa có:

- Cấu trúc entity list trong RAM host và cách duyệt nó
- HP/tên/loại của thực thể xung quanh, cách phân biệt boss với quái thường và người chơi
- Thời gian hồi sinh boss để lập lịch đi săn

Phương án dự phòng nếu không đọc được entity list: boss spawn ở tọa độ cố định nên chỉ cần calibrate bãi spawn một lần, đến nơi rồi kiểm tra trên màn hình/minimap (chấm đỏ, thanh HP boss) bằng template matching. Cách này kém chính xác hơn đọc RAM và chưa được xây dựng.

### 4. Các điểm nghẽn vận hành nhỏ hơn

- Trong số 42 cặp X/Y ứng viên, đa số là trùng ngẫu nhiên; hiện vẫn phải chọn tay cặp đúng (gợi ý: các cặp dùng chung một địa chỉ Y trông giống mảng struct hơn). Chưa có bước tự xác thực cặp đúng bằng cách đọc lại sau khi nhân vật di chuyển
- Gõ tiếng Việt có dấu qua adb vào chat game chưa đáng tin cậy (đã thử encode UTF-8 dạng bytes để tránh lỗi console Windows), liên quan nếu quay lại phương án link chat
- Lỗi quoting khi dùng `adb shell su`: `cmd` của Windows cắt mất dấu ngoặc kép bên trong — mẫu chạy ổn là `echo <lệnh> | adb shell su` kết hợp `findstr` ở phía local. Lỗi này từng gây chẩn đoán sai "không thấy tiến trình game"

## Câu hỏi cụ thể nhờ Claude Code xem giúp

1. **Khử việc săn địa chỉ mỗi phiên:** khi pointer chain phía host đã kết luận là 0 đường, còn kỹ thuật nào khác để tự động định vị lại HP và cặp X/Y sau mỗi lần khởi động giả lập không — ví dụ quét theo mẫu byte (AOB/signature scan) quanh cấu trúc đã biết, hoặc nhận diện struct bằng các field kề nhau có quan hệ cố định?

2. **Tự xác thực cặp X/Y đúng:** từ 42 cặp ứng viên, làm sao lọc tự động cặp thật mà không cần người chọn tay — chẳng hạn đọc lại sau một lần di chuyển nhỏ và giữ cặp thay đổi khớp với số tile game hiển thị?

3. **Entity list phía host:** có phương pháp hệ thống nào để tìm cấu trúc danh sách thực thể (boss/quái xung quanh) trong RAM của `Ld9BoxHeadless.exe` khi không có pointer chain và mã IL2CPP đã obfuscate không? Nên bắt đầu từ mỏ neo `CSMainPlayerAction.Instance` / `mainPlayerTrans` offset `0x10` như thế nào?

4. **Giải thích hiện tượng trong-guest:** vì sao đọc `/proc/<pid>/mem` bằng root không bao giờ thấy giá trị HP dù cùng giá trị đó đọc được từ phía host? Có phải do cách LDPlayer map bộ nhớ guest hay do Unity tách vùng nhớ?

5. **Công thức tap trên bản đồ:** với screenshot bản đồ đang mở và tọa độ tile hiện tại/đích, cách suy ra điểm gốc và tỉ lệ quy đổi tile → pixel một cách tin cậy là gì, và cần calibrate những điểm mốc nào (tối thiểu) để tính được?

6. **Vị trí float world vs tile nguyên:** làm sao kiểm chứng giả thuyết "vị trí thật là float world, tile là giá trị hiển thị" — tìm cặp float thay đổi tương ứng khi nhân vật di chuyển như thế nào trong RAM host?

## Các file và báo cáo liên quan

- Báo cáo mổ SmartPK: `~/workspace/smartpk-analysis/BAO-CAO-SMARTPK.md`
- Báo cáo mổ 360Auto: `~/workspace/auto360-analysis/BAO-CAO-360AUTO.md`
- Dump IL2CPP (script/dump đầu ra Il2CppDumper): `~/workspace/il2cpp/`
- Tool follow: `~/workspace/mu-follow/`
- Các script đang dùng: `quet_hp_host.py` (tìm HP, lưu `hp_addr.txt`), `vong_lap_tu_hoi_sinh.py` (vòng lặp tự hồi sinh), `tim_toa_do.py` (tìm cặp X/Y, lưu `toa_do_addr.txt`), `ghi_toa_do.py` (ghi waypoint vào `waypoints.txt`), `di_den_ban_do.py` (di chuyển bằng click bản đồ), `calib_nut.py` (calibrate vị trí nút)
