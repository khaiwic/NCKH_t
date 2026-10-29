$ErrorActionPreference = 'Stop'
$outDir = $PSScriptRoot
$ppt = New-Object -ComObject PowerPoint.Application
$deck = $null
function Color([string]$hex) {
    $r = [Convert]::ToInt32($hex.Substring(0,2),16)
    $g = [Convert]::ToInt32($hex.Substring(2,2),16)
    $b = [Convert]::ToInt32($hex.Substring(4,2),16)
    return $r + 256*$g + 65536*$b
}
function Box($s,$x,$y,$w,$h,$fill='FFFFFF',$stroke='FFFFFF',$radius=$false) {
    $type = if ($radius) { 5 } else { 1 }
    $shape = $s.Shapes.AddShape($type,$x,$y,$w,$h)
    $shape.Fill.ForeColor.RGB = Color $fill
    $shape.Line.ForeColor.RGB = Color $stroke
    $shape.Line.Weight = 0.8
    return $shape
}
function Txt($s,$text,$x,$y,$w,$h,$size=18,$bold=$false,$color='202020',$align=1) {
    $shape = $s.Shapes.AddTextbox(1,$x,$y,$w,$h)
    $shape.TextFrame.MarginLeft=0; $shape.TextFrame.MarginRight=0
    $shape.TextFrame.MarginTop=0; $shape.TextFrame.MarginBottom=0
    $shape.TextFrame.WordWrap=-1
    $shape.TextFrame.AutoSize=0
    $shape.TextFrame.TextRange.Text=$text
    $shape.TextFrame.TextRange.Font.Name='Arial'
    $shape.TextFrame.TextRange.Font.Size=[single]$size
    $shape.TextFrame.TextRange.Font.Bold=$(if($bold){-1}else{0})
    $shape.TextFrame.TextRange.Font.Color.RGB=Color $color
    $shape.TextFrame.TextRange.ParagraphFormat.SpaceAfter=0
    $shape.TextFrame.TextRange.ParagraphFormat.Alignment=$align
    # Bake line breaks into the text: Canva does not retain PowerPoint auto-wrap.
    $shape.TextFrame.WordWrap=0
    $wrapped=[Collections.Generic.List[string]]::new()
    foreach($paragraph in ($text -split '\r?\n')) {
        $current=''
        foreach($word in ($paragraph -split '\s+')) {
            $candidate=if($current){$current+' '+$word}else{$word}
            $shape.TextFrame.TextRange.Text=$candidate
            if($current -and $shape.TextFrame.TextRange.BoundWidth -gt ($w-8)) {
                $wrapped.Add($current)
                $current=$word
            } else {$current=$candidate}
        }
        $wrapped.Add($current)
    }
    $shape.TextFrame.TextRange.Text=($wrapped -join "`n")
    $shape.TextFrame.TextRange.Font.Name='Arial'
    $shape.TextFrame.TextRange.Font.Size=[single]$size
    $shape.TextFrame.TextRange.Font.Bold=$(if($bold){-1}else{0})
    $shape.TextFrame.TextRange.Font.Color.RGB=Color $color
    $shape.TextFrame.TextRange.ParagraphFormat.Alignment=$align
    return $shape
}
function Line($s,$x1,$y1,$x2,$y2,$color='EE1010',$weight=2,$arrow=$false) {
    # Thin rectangles retain horizontal/vertical geometry through Canva import.
    $length=[Math]::Sqrt(($x2-$x1)*($x2-$x1)+($y2-$y1)*($y2-$y1))
    $angle=[Math]::Atan2(($y2-$y1),($x2-$x1))*180/[Math]::PI
    $shape=$s.Shapes.AddShape(1,(($x1+$x2)/2-$length/2),(($y1+$y2)/2-$weight/2),$length,$weight)
    $shape.Fill.ForeColor.RGB=Color $color
    $shape.Line.Visible=0
    $shape.Rotation=[single]$angle
    if($arrow){
        $tip=$s.Shapes.AddShape(7,($x2-5),($y2-5),10,10)
        $tip.Fill.ForeColor.RGB=Color $color
        $tip.Line.Visible=0
        $tip.Rotation=[single]($angle+90)
    }
    return $shape
}
function Dot($s,$x,$y,$r=5,$fill='EE1010') {
    $shape=$s.Shapes.AddShape(9,$x-$r,$y-$r,2*$r,2*$r)
    $shape.Fill.ForeColor.RGB=Color $fill
    $shape.Line.Visible=0
    return $shape
}
function Base($title,$number,$source) {
    $s=$deck.Slides.Add($deck.Slides.Count+1,12)
    $s.FollowMasterBackground=0
    $s.Background.Fill.ForeColor.RGB=Color 'FFFFFF'
    [void](Box $s 0 0 960 134 'ED1010' 'ED1010')
    [void](Line $s 39 0 39 129 'FFC2C2' 1)
    [void](Line $s 75 131 158 131 'FFAAAA' 1)
    [void](Txt $s $title 58 20 810 102 34 $true 'FFFFFF')
    [void](Txt $s 'CHƯƠNG III' 814 108 125 17 10 $true 'FFE5E5' 3)
    [void](Line $s 35 510 925 510 'E6E6E6' 0.7)
    [void](Txt $s $source 35 519 825 15 9 $false '666666')
    [void](Txt $s "$number / 13" 860 517 65 18 11 $false '777777' 3)
    return $s
}
function Block($s,$title,$body,$y,$height=73) {
    [void](Txt $s $title 475 $y 440 25 19 $true '202020')
    [void](Txt $s $body 475 ($y+26) 440 ($height-24) 17.5)
}
function Grid($s,$x,$y,$astar=$false) {
    $cell=22
    $blocked=@('3,0','3,1','3,2','3,3','3,4')
    $route=@(@(0,2),@(1,2),@(2,2),@(2,3),@(2,4),@(2,5),@(3,5),@(4,5),@(5,5),@(6,5),@(7,5),@(7,4),@(7,3),@(7,2))
    for($r=0;$r -lt 7;$r++) {
        for($c=0;$c -lt 8;$c++) {
            $fill='FFFFFF'
            if($blocked -contains "$c,$r"){$fill='555555'}
            elseif((!$astar -and ($c -lt 3 -or $r -ge 4 -or $c -ge 6)) -or ($astar -and (($c -le 2 -and $r -ge 2 -and $r -le 5) -or ($r -eq 5) -or ($c -eq 7 -and $r -ge 2)))) {$fill='F9DEDE'}
            [void](Box $s ($x+$c*$cell) ($y+$r*$cell) $cell $cell $fill 'D6D6D6')
        }
    }
    for($i=1;$i -lt $route.Count;$i++){
        [void](Line $s ($x+($route[$i-1][0]+0.5)*$cell) ($y+($route[$i-1][1]+0.5)*$cell) ($x+($route[$i][0]+0.5)*$cell) ($y+($route[$i][1]+0.5)*$cell) 'E91010' 2.7)
    }
    [void](Dot $s ($x+11) ($y+55) 5 '222222')
    [void](Dot $s ($x+165) ($y+55) 5 '198755')
}
try {
    $deck=$ppt.Presentations.Add(0)
    $deck.PageSetup.SlideWidth=960
    $deck.PageSetup.SlideHeight=540

    $s=Base "3.1 Tìm đường trên đồ thị`nDijkstra và A*" 10 'Nguồn: main.tex, mục 3.1 • Sơ đồ nguyên lý, không phải kết quả so sánh mô phỏng.'
    [void](Txt $s 'Dijkstra' 52 166 175 24 18 $true '202020' 2)
    [void](Txt $s 'A*' 253 166 175 24 18 $true '202020' 2)
    Grid $s 52 207 $false
    Grid $s 253 207 $true
    [void](Dot $s 66 385 5 'F1BABA')
    [void](Txt $s 'Vùng đã xét' 78 376 130 23 13)
    [void](Box $s 222 380 10 10 '555555' '555555')
    [void](Txt $s 'Vật cản' 240 376 80 23 13)
    [void](Line $s 325 385 345 385 'E91010' 2.7)
    [void](Txt $s 'Đường đi' 353 376 80 23 13)
    [void](Box $s 52 417 377 65 'FFF0F0' 'FFF0F0' $true)
    [void](Txt $s "Dijkstra: chọn chi phí g nhỏ nhất`nA*: chọn f = g + h nhỏ nhất" 67 428 347 47 17 $true 'B70C0C')
    Block $s 'Biểu diễn bản đồ' 'Chia ô lưới, nối các ô tự do lân cận; xét kích thước xe và khoảng dự phòng.' 155 78
    Block $s 'Dijkstra' 'Mở rộng theo g. Tìm đường tối ưu trên đồ thị khi trọng số cạnh không âm.' 239 77
    Block $s 'A*' 'Bổ sung heuristic h để hướng tới đích; chọn h phù hợp trọng số và bước đi.' 322 77
    Block $s 'Liên hệ với xe ba bánh' 'Đường gấp khúc cần làm mượt, kiểm tra lại va chạm và gán vận tốc trước khi bám.' 405 88

    $s=Base "3.2 Lấy mẫu ngẫu nhiên`nPRM, RRT và RRT*" 11 'Nguồn: main.tex, mục 3.2 • Minh họa cấu trúc mạng và cây tìm kiếm.'
    [void](Txt $s 'PRM: xây mạng rồi truy vấn' 52 158 377 25 17 $true)
    [void](Box $s 214 225 50 50 '666666' '666666')
    $pts=@(@(70,235),@(112,192),@(168,187),@(193,219),@(135,270),@(184,307),@(274,189),@(324,212),@(365,269),@(283,311),@(337,310),@(407,238))
    $edges=@(@(0,1),@(0,4),@(1,2),@(2,3),@(3,4),@(4,5),@(2,6),@(6,7),@(7,8),@(8,9),@(9,10),@(8,10),@(8,11),@(7,11),@(5,9))
    foreach($e in $edges){[void](Line $s $pts[$e[0]][0] $pts[$e[0]][1] $pts[$e[1]][0] $pts[$e[1]][1] 'B4B4B4' 1.2)}
    foreach($i in @(0,1,2,6,7,11)) {if($i -ne 0){$prev=@{1=0;2=1;6=2;7=6;11=7}[$i];[void](Line $s $pts[$prev][0] $pts[$prev][1] $pts[$i][0] $pts[$i][1] 'E91010' 2.6)}}
    foreach($p in $pts){[void](Dot $s $p[0] $p[1] 3.5 '777777')}
    [void](Dot $s 70 235 5 '222222'); [void](Dot $s 407 238 5 '198755')
    [void](Txt $s 'RRT → RRT*: phát triển và cải thiện cây' 52 345 390 24 16 $true)
    $tree=@(@(70,458),@(126,423),@(176,448),@(224,415),@(282,443),@(337,410),@(402,433),@(150,383),@(240,375),@(360,477))
    $branches=@(@(0,1),@(1,2),@(3,4),@(5,6),@(1,7),@(3,8),@(4,9))
    foreach($e in $branches){[void](Line $s $tree[$e[0]][0] $tree[$e[0]][1] $tree[$e[1]][0] $tree[$e[1]][1] 'A0A0A0' 1.8)}
    [void](Line $s 126 423 224 415 'E91010' 2.8)
    [void](Line $s 224 415 337 410 'E91010' 2.8)
    [void](Txt $s 'Nối lại nhánh khi chi phí tốt hơn' 130 474 300 20 12 $false 'B70C0C')
    foreach($p in $tree){[void](Dot $s $p[0] $p[1] 3.5 '666666')}
    Block $s 'PRM — phù hợp nhiều truy vấn' 'Lấy mẫu hợp lệ, nối thành mạng; dùng Dijkstra/A* tìm đường từ đầu đến đích.' 155 87
    Block $s 'RRT — tìm đường khả thi' 'Lấy mẫu → tìm đỉnh gần nhất → mở rộng. Chỉ thêm chuyển động không va chạm.' 251 87
    Block $s 'RRT* — cải thiện chi phí' 'Chọn cha tốt nhất và nối lại nhánh; cần thêm thời gian kiểm tra và cập nhật cây.' 347 87
    [void](Box $s 475 443 440 52 'FFF0F0' 'FFF0F0' $true)
    [void](Txt $s 'Tối ưu tiệm cận có điều kiện; hữu hạn mẫu chưa bảo đảm lời giải tối ưu.' 487 451 416 39 15.5 $true 'B70C0C')

    $s=Base "3.3 Trường thế nhân tạo (APF)`nNguyên lý hút–đẩy" 12 'Nguồn: main.tex, mục 3.3.1 • Lực ảo là hướng dẫn chuyển động, không phải lực cơ học.'
    [void](Dot $s 118 227 43 'D9D9D9')
    [void](Txt $s 'Vật cản' 75 214 86 25 16 $true '444444' 2)
    [void](Dot $s 210 335 13 '235875')
    [void](Txt $s 'Robot' 158 350 75 23 15 $true '235875')
    [void](Dot $s 398 224 8 '198755')
    [void](Txt $s 'Đích' 369 194 60 25 17 $true '198755')
    [void](Line $s 219 329 369 241 '198755' 3.2 $true)
    [void](Txt $s 'F hút' 271 252 85 24 17 $true '198755')
    [void](Line $s 217 345 267 411 '276AA0' 3.2 $true)
    [void](Txt $s 'F đẩy' 269 390 90 24 17 $true '276AA0')
    [void](Line $s 225 335 405 335 'E91010' 4 $true)
    [void](Txt $s 'F tổng' 323 305 90 24 18 $true 'D51010')
    [void](Box $s 52 445 377 47 'FFF0F0' 'FFF0F0' $true)
    [void](Txt $s 'F tổng = F hút + Σ F đẩy' 67 456 347 27 21 $true 'B70C0C' 2)
    Block $s 'Thế hút và thế đẩy' 'Đích tạo hướng hút; vật cản tạo hướng đẩy trong khoảng tác động đã chọn.' 155 77
    Block $s 'Cập nhật theo trạng thái hiện tại' 'Tính hướng từ tổng lực ảo, giới hạn bước và kiểm tra cả đoạn chuyển động.' 238 78
    Block $s 'Áp dụng cho xe vi sai' 'Chuyển hướng trường lực thành lệnh vận tốc tiến và vận tốc quay; xe không đi ngang.' 322 80
    Block $s 'Đặc điểm' 'Thuận tiện phản ứng cục bộ; chất lượng phụ thuộc tham số, bản đồ và các điểm cân bằng.' 408 82

    $s=Base "3.3 Hạn chế APF`nCực tiểu cục bộ và hướng khắc phục" 13 'Nguồn: main.tex, mục 3.3.2 • Các giải pháp hỗ trợ cần được kiểm chứng.'
    [void](Box $s 52 155 377 177 'FFFFFF' 'E5E5E5' $true)
    [void](Txt $s 'Cực tiểu cục bộ' 66 165 340 22 16 $true)
    [void](Box $s 103 199 14 82 '666666' '666666')
    [void](Box $s 233 199 14 82 '666666' '666666')
    [void](Box $s 103 267 144 14 '666666' '666666')
    [void](Dot $s 175 237 7 '235875')
    [void](Line $s 175 246 175 262 '198755' 2.5 $true)
    [void](Line $s 175 228 175 208 '276AA0' 2.5 $true)
    [void](Dot $s 175 308 5 '198755')
    [void](Txt $s 'Đích' 188 298 45 20 12 $false '198755')
    [void](Txt $s "Lực hút và đẩy`ncân bằng trước đích" 269 215 145 62 16)
    [void](Txt $s 'F hút + F đẩy ≈ 0' 269 280 145 25 15 $true 'B70C0C')
    [void](Box $s 52 349 377 144 'FFFFFF' 'E5E5E5' $true)
    [void](Txt $s 'Đích gần vật cản (GNRON)' 66 360 340 22 16 $true)
    [void](Dot $s 333 429 29 'D9D9D9')
    [void](Dot $s 290 429 5 '198755')
    [void](Txt $s 'Đích' 274 446 50 20 12 $false '198755')
    [void](Dot $s 123 429 7 '235875')
    [void](Line $s 135 421 254 421 '198755' 2.5 $true)
    [void](Line $s 270 437 186 437 '276AA0' 2.5 $true)
    [void](Txt $s 'Lực đẩy còn tác động khi tới gần đích' 66 472 348 18 12 $false '666666')
    Block $s 'Cực tiểu cục bộ' 'Xe có thể dừng trước đích khi lực hút và lực đẩy cân bằng, ví dụ vật cản chữ U.' 155 84
    Block $s 'GNRON' 'Đích hợp lệ ở gần vật cản có thể chịu lực đẩy còn dư, khiến xe khó tiếp cận.' 247 80
    Block $s 'Các hướng khắc phục' 'Sửa thế đẩy theo khoảng cách tới đích; bổ sung lực ảo tiếp tuyến khi phát hiện mắc kẹt.' 335 91
    [void](Box $s 475 444 440 50 'FFF0F0' 'FFF0F0' $true)
    [void](Txt $s 'Luôn giới hạn vận tốc, kiểm tra va chạm và theo dõi tiến triển tới đích.' 487 452 416 38 15.5 $true 'B70C0C')

    $notes=@(
        'Nguồn: main.tex, mục 3.1. Trình bày bản đồ đã xét kích thước robot. Dijkstra tối ưu trên đồ thị với trọng số không âm. A* dùng f=g+h; heuristic chấp nhận được không vượt chi phí tối ưu còn lại. Với heuristic nhất quán, đỉnh đã đóng không cần mở lại; nếu chỉ chấp nhận được thì cần cho phép mở lại khi có g tốt hơn. Hai lưới chỉ minh họa nguyên lý, không phải kết quả đo hay kết quả mục 3.4.',
        'Nguồn: main.tex, mục 3.2. Phân biệt PRM dùng mạng cho nhiều truy vấn và RRT thường giải một truy vấn. RRT* thêm chọn cha và nối lại nhánh; cập nhật chi phí hậu duệ và giữ cấu trúc cây không có chu trình. Tính tối ưu tiệm cận cần các giả thiết về khoảng hở, lấy mẫu và kết nối; không bảo đảm tối ưu sau hữu hạn mẫu. Mọi cạnh phải được kiểm tra trên toàn chuyển động.',
        'Nguồn: main.tex, mục 3.3.1. APF dùng âm gradient của tổng thế hút và thế đẩy. F trong sơ đồ là hướng dẫn chuyển động. Với xe vi sai, chuyển hướng trường lực thành hướng mong muốn và lệnh v, omega; không áp lực như một vận tốc ngang độc lập. Phải giới hạn lệnh và kiểm tra cả đoạn di chuyển, không chỉ hai điểm đầu cuối.',
        'Nguồn: main.tex, mục 3.3.2. Cực tiểu cục bộ khiến robot chưa tới đích đã dừng. GNRON xét đích hợp lệ gần vật cản; đích trong vùng cấm vẫn không tiếp cận an toàn. Có thể sửa thế đẩy theo khoảng cách đích và đề xuất lực ảo tiếp tuyến khi mắc kẹt. Sửa GNRON không loại mọi cực tiểu, lực ảo không bảo đảm đầy đủ hoặc tối ưu. Nội dung là nguyên lý và hướng khắc phục, chưa đưa kết quả mô phỏng của mục 3.4.'
    )
    for($i=1;$i -le 4;$i++){
        $deck.Slides.Item($i).NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text=$notes[$i-1]
    }
    $pptx=Join-Path $outDir 'Chuong_III_4_slides.pptx'
    $deck.SaveAs($pptx,24)
    for($i=1;$i -le 4;$i++){
        $deck.Slides.Item($i).Export((Join-Path $outDir "slide_$i.png"),'PNG',1920,1080)
    }
    Write-Output "Created: $pptx"
    Write-Output ('Slides: '+$deck.Slides.Count)
} finally {
    if($null -ne $deck){$deck.Close()}
    $ppt.Quit()
    [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($ppt)
}
