from bs4 import BeautifulSoup
import csv
import os
from PIL import Image
import qrcode
import requests
from typing import List

def get_artwork(code: str):
    img_filename = f"content/{code}_img.jpg"
    qr_filename = f"content/{code}_qr.jpg"
    url = f"https://www.platform-a.art/work@{code}"

    # Download image
    if os.path.exists(img_filename) and os.path.exists(qr_filename):
        print(f'{code}: already downloaded')
        return
    
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    element = soup.find(attrs={"property": "og:image"})

    if not element:
        raise Exception("image element not found")
    
    img_url = element.attrs['content']
    response = requests.get(img_url)
    if response.status_code == 200:
        # Open a file in binary write mode and save the image
        with open(img_filename, 'wb') as file:
            file.write(response.content)
    else:
        raise Exception("couldn't download image")
        
    # Generate the QR code
    qr = qrcode.QRCode(
       version=1,
       error_correction=qrcode.constants.ERROR_CORRECT_L,
       box_size=10,
       border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    img = img.convert("RGB")  # Convert to RGB mode
    img.save(qr_filename)

def get_artworks(codes: List[str]):
    for code in codes:
        try:
            get_artwork(code)
            print(f'{code} done.')
        except Exception as e:
            print(f'{code} failed: {e}')

template=r"""\documentclass{article}
\RequirePackage{graphicx}
\RequirePackage{geometry}
\RequirePackage{etoolbox}
\RequirePackage[most]{tcolorbox}
\RequirePackage{setspace}
\RequirePackage{fontspec}
\RequirePackage{xeCJK}
\setmainfont[Path = /platform-a/]{NotoSansCJK-Regular.ttc}
\setCJKmainfont[Path = /platform-a/]{NotoSansCJK-Regular.ttc}


\geometry{
	a4paper,
	landscape,
	margin=0in
}

\newcommand{\stickerwidth}{42.3mm}
\newcommand{\stickerheight}{105mm}
\newcommand{\imagesize}{32mm}
\newcommand{\qrsize}{20mm}


\newcommand{\sticker}[7] {
	% #1: 作品名稱
	% #2: 藝術家
	% #3: code
	% #4: 媒材
	% #5: 作品尺寸(高)
	% #6: 作品尺寸(寬)
	% #7: 作品售價NTD
	
	\begin{tcolorbox}[
		width=\stickerwidth,
		height=\stickerheight,
		colframe=white,
		colback=white,
		sharp corners,
		boxsep=0pt,
		left=0pt, right=0pt, bottom=0pt, top=0pt,
		boxrule=0pt,
		valign=top,
		halign=center]
		
		\vspace{4mm}
		\begin{minipage}[c][\imagesize]{\textwidth}
			\centering
			
			\includegraphics[width=\imagesize,height=\imagesize,keepaspectratio]{content/#3_img.jpg} % Image
		\end{minipage}
		
		\begin{minipage}[t][10mm]{\imagesize}
			\centering
			\vspace{5mm}
			#1
		\end{minipage}
		
		\begin{minipage}[b][35mm]{\imagesize}
			\centering
			#2
			
			\vspace{2mm}
			
			#4
			
			\vspace{2mm}
			
			#7 NTD
			
			\vspace{3mm}
		\end{minipage}
		
		\begin{minipage}[b]{\textwidth}
			\centering
			\includegraphics[width=\qrsize]{content/#3_qr.jpg} % Qr code
		\end{minipage}
		
		\vspace{1cm}		
		
		
	\end{tcolorbox}
}

\begin{document}
	\pagestyle{empty} % Removes page numbers

\begin{flushleft}
	\begin{tcbitemize}[raster columns=7,
					   raster equal height,
					   raster row skip=0mm,
					   raster column skip=0mm,
					   colback=white,
					   colframe=white,
					   size=tight,
					   boxrule=0pt,
					   boxsep=0pt,
					   halign=center,
					   valign=center]					   
###WORKS###
	\end{tcbitemize}
\end{flushleft}

\end{document}"""

artist_alias = {
    '賈瑞云': '慕蘭',
    '簡翊晉': '版畫職男',
    '何珞瑜': '雷',
    '謝佳淇': 'Hannah Shieh',
    '林宜蓁': 'YI CHEN LIN',
    '童于洋': '魚羊',
    '王貽宣': '王蟻宣',
    '張育華': '鴨寶',
    '王淑靜': 'MEI',
    '楊舒涵': '楊舒涵 內向陌生人',
    '羅昱翰': '四維羅',
    '涂恩華': 'tuenhua'    
}

# columns:
#  0 作品名稱
#  1 藝術家
#  2 code
#  3 媒材
#  4 作品尺寸(高)
#  5 作品尺寸(寬)
#  6 作品售價NTD

os.chdir('works')

with open('works.csv', 'r') as f:
    reader = csv.reader(f)
    works = [row for row in csv.reader(f)][1:]

codes = [w[2] for w in works]
get_artworks(codes)

for work in works:
    # Change real name to alias where necessary
    if work[1] in artist_alias:
        work[1] = artist_alias[work[1]]

    # Add mboxes around each word in medium to prevent them breaking
    # if the line is too long.
    # "彩、木" The second character is "、" but for some reason it gets displayed
    # differently when it's not surrounded by chinese text.
    work[3] = '、'.join([f'\\mbox{{{m}}}' for m in work[3].split('、')])
    
tex_lines = '\n'.join([f'\\tcbitem \\sticker{{{w[0].replace("#", "\\#")}}}{{{w[1]}}}{{{w[2]}}}{{{w[3]}}}{{{w[4]}}}{{{w[5]}}}{{{w[6]}}}' for w in works])
tex = (template.replace("###WORKS###", tex_lines))

with open('GENERATED.tex', 'w') as file:
    file.write(tex)

os.system('xelatex -synctex=1 -interaction=nonstopmode GENERATED.tex')