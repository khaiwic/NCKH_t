$ErrorActionPreference = 'Stop'
$outDir = $PSScriptRoot
$helperPath = Join-Path $PSScriptRoot '..\slides_chuong_III\build_slides.ps1'
$parseTokens = $null
$parseErrors = $null
$ast = [Management.Automation.Language.Parser]::ParseFile($helperPath,[ref]$parseTokens,[ref]$parseErrors)
if($parseErrors.Count){throw 'Cannot parse the existing slide drawing helpers.'}
$helperNames = @('Color','Box','Txt','Line','Dot','Base','Block')
foreach($functionAst in $ast.FindAll({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst]},$false)) {
    if($functionAst.Name -in $helperNames) {
        $functionText = $functionAst.Extent.Text
        if($functionAst.Name -eq 'Base') {
            $functionText = $functionText.Replace('CHƯƠNG III','CHƯƠNG IV').Replace('/ 13','/ 19')
        }
        . ([scriptblock]::Create($functionText))
    }
}
$ppt = New-Object -ComObject PowerPoint.Application
$deck = $null
function FlowBox($s,$title,$x,$y,$w,$h,$accent=$false) {
    $fill = if($accent){'FFF0F0'}else{'F6F6F6'}
    [void](Box $s $x $y $w $h $fill $fill $true)
    [void](Txt $s $title ($x+12) ($y+9) ($w-24) ($h-12) 16 $true '333333' 2)
}
try {
    $deck = $ppt.Presentations.Add(0)
    $deck.PageSetup.SlideWidth = 960
    $deck.PageSetup.SlideHeight = 540

    # Four visibly empty white pages reserved for the user's future section 3.4.
    for($i=1;$i -le 4;$i++) {
        $blank = $deck.Slides.Add($deck.Slides.Count+1,12)
        $blank.FollowMasterBackground = 0
        $blank.Background.Fill.ForeColor.RGB = Color 'FFFFFF'
        [void](Box $blank 0 0 960 540 'FFFFFF' 'FFFFFF')
    }

    $s = Base "4.2 Kiến trúc điều khiển`nbám quỹ đạo" 18 'Nguồn: main.tex, mục 4.2 • Kiến trúc đề xuất; hệ số điều khiển được chốt sau thử nghiệm.'
    FlowBox $s 'Đường tham chiếu + tư thế ước lượng' 80 158 335 43
    [void](Line $s 247 202 247 215 'BB1010' 2 $true)
    FlowBox $s "Pure Pursuit`nVận tốc thân xe (vc, ωc)" 80 220 335 56 $true
    [void](Line $s 247 277 247 289 'BB1010' 2 $true)
    FlowBox $s "Đổi lệnh vận tốc hai bánh`nvR = vc + Lωc/2; vL = vc − Lωc/2" 80 295 335 57
    [void](Line $s 247 353 247 365 'BB1010' 2 $true)
    FlowBox $s "PI/PID → PWM → TB6612`nĐộng cơ hai bánh" 80 371 335 56 $true
    [void](Line $s 247 428 247 440 'BB1010' 2 $true)
    FlowBox $s "Encoder`nVận tốc đo / Odometry" 80 446 335 51
    [void](Line $s 80 471 48 471 '777777' 1.6)
    [void](Line $s 48 471 48 247 '777777' 1.6)
    [void](Line $s 48 247 77 247 '777777' 1.6 $true)
    [void](Line $s 48 398 77 398 '777777' 1.6 $true)
    Block $s 'Vòng ngoài: Pure Pursuit' 'Chọn điểm nhìn trước trên đường; tạo vận tốc thân xe từ tham chiếu và tư thế ước lượng.' 155 79
    Block $s 'Quy đổi vận tốc hai bánh' "vR = vc + Lωc/2; vL = vc − Lωc/2.`nL là khoảng cách hai bánh chủ động." 240 79
    Block $s 'Vòng trong: PI/PID và PWM' 'Mỗi bánh dùng phản hồi encoder; khởi đầu với PI và giới hạn duty trước khi đưa tới driver.' 325 79
    Block $s 'Giới hạn và điều kiện thực thi' 'Xét vận tốc, gia tốc; giảm đồng thời hai lệnh khi quá tốc bánh. Dừng nếu đường không còn hợp lệ.' 410 84
    $s.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = 'Nguồn duy nhất: main.tex, mục 4.2. Đây là kiến trúc đề xuất hai cấp. Vòng ngoài Pure Pursuit dùng điểm nhìn trước và tư thế ước lượng để tạo vc, omega_c. Độ cong kappa_pp = 2 y_g^R / ell^2, với ell > 0; gần đích phải dùng khoảng cách thực và tránh chia cho số quá nhỏ. Vận tốc hai bánh: vR_ref = vc + L omega_c / 2, vL_ref = vc - L omega_c / 2. Vòng trong PI/PID nhận sai số vận tốc từ encoder, giới hạn duty PWM và truyền lệnh qua TB6612. PI được chọn khởi đầu; chưa có hệ số cụ thể được xác nhận. Khi quá giới hạn bánh, giảm chung hai lệnh, sau đó vẫn kiểm tra gia tốc. Bộ bám không tự tìm đường tránh vật cản mới; nếu đường không còn hợp lệ thì dừng hoặc yêu cầu quy hoạch lại. Pure Pursuit chủ yếu bám hình học, không tự bảo đảm đồng bộ thời gian.'

    $s = Base "4.3 Kết quả thực nghiệm`nvà đánh giá sai số" 19 'Nguồn: main.tex, mục 4.3 • Hiện trình bày quy trình, tiêu chí và biểu mẫu thực nghiệm.'
    [void](Box $s 52 155 377 70 'F6F6F6' 'F6F6F6' $true)
    [void](Txt $s 'Kịch bản 1: bám đường định sẵn' 66 166 350 24 17 $true)
    [void](Txt $s 'Đường thẳng và đường cong chữ S.' 66 195 350 23 16)
    [void](Box $s 52 239 377 84 'F6F6F6' 'F6F6F6' $true)
    [void](Txt $s 'Kịch bản 2: đi tránh vật cản' 66 250 350 24 17 $true)
    [void](Txt $s 'Vật cản tĩnh đã đo và nhập bản đồ; kiểm tra đường trước khi chạy.' 66 279 350 39 16)
    [void](Txt $s 'Biểu mẫu đánh giá' 52 339 377 25 18 $true)
    [void](Box $s 52 374 377 29 'EEEEEE' 'EEEEEE')
    [void](Txt $s 'Chỉ tiêu' 65 379 234 20 14 $true)
    [void](Txt $s 'Trạng thái' 305 379 112 20 14 $true)
    $rows = @(
        @('RMSE vị trí đối chứng','Chưa đo'),
        @('Thời gian hoàn thành','Chưa đo'),
        @('Tỷ lệ thành công','Chưa đo')
    )
    for($i=0;$i -lt $rows.Count;$i++) {
        $rowY = 407 + $i*29
        [void](Txt $s $rows[$i][0] 65 $rowY 234 23 14)
        [void](Txt $s $rows[$i][1] 305 $rowY 112 23 14 $true 'B70C0C')
        [void](Line $s 52 ($rowY+25) 429 ($rowY+25) 'E3E3E3' 0.6)
    }
    Block $s 'Thống nhất điều kiện thử' 'Chốt hình học xe, số đếm encoder, điều khiển, tải, nguồn và mặt sàn trước đợt đo.' 155 80
    Block $s 'Ghi dữ liệu và đo đối chứng' 'Lưu encoder, tốc độ đặt/đo, PWM, Odometry; dùng camera hoặc mốc đo đánh giá vị trí thực.' 242 83
    Block $s 'Các chỉ tiêu cần đánh giá' 'Sai số vị trí, ngang, hướng và điểm cuối; thời gian hoàn thành, tỷ lệ thành công, PWM bão hòa.' 332 88
    [void](Box $s 475 441 440 55 'FFF0F0' 'FFF0F0' $true)
    [void](Txt $s 'Chưa có dữ liệu chạy robot; các bảng chưa dùng để kết luận định lượng.' 488 451 414 38 15.5 $true 'B70C0C')
    $s.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = 'Nguồn duy nhất: main.tex, mục 4.3. Báo cáo nêu rõ chưa có dữ liệu chạy robot, các bảng là biểu mẫu thực nghiệm. Không trình bày bất kỳ số đo hay kết quả suy diễn nào. Kịch bản 1 gồm đường thẳng và đường cong hình chữ S trong mặt phẳng; chữ S ở đây khác profile vận tốc chữ S. Kịch bản 2 dùng vật cản tĩnh đã đo và nhập bản đồ vì cấu hình hiện tại chỉ có encoder; không giả định khả năng tự phát hiện vật cản chưa biết. Cần lưu đầy đủ các lượt, kể cả thất bại. Nhật ký gồm thời gian, encoder, tốc độ đặt/đo, PWM, Odometry và trạng thái điều khiển. Đánh giá vị trí thực cần đo đối chứng; riêng encoder chưa đủ chứng minh độ chính xác vị trí thật. RMSE theo thời gian cần dữ liệu đồng bộ và lịch tham chiếu tương ứng. Các chỉ tiêu còn gồm sai số ngang, hướng, cuối, thời gian, khoảng hở và bão hòa PWM. Các ô Chưa đo giữ đúng trạng thái báo cáo.'

    $pptx = Join-Path $outDir '4_trang_trang_va_slide_4_2_4_3.pptx'
    $deck.SaveAs($pptx,24)
    for($i=1;$i -le $deck.Slides.Count;$i++) {
        $deck.Slides.Item($i).Export((Join-Path $outDir "slide_$i.png"),'PNG',1920,1080)
    }
    Write-Output "Created: $pptx"
    Write-Output ('Slides: '+$deck.Slides.Count+' (4 white pages + sections 4.2 and 4.3)')
} finally {
    if($null -ne $deck){$deck.Close()}
    $ppt.Quit()
    [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($ppt)
}
