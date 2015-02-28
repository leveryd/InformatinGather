#encoding=gbk

words = []
with open('pinyin.txt') as inFile:
    while True:
        word = inFile.readline().strip().split(' ')
        if len(word) < 2: break
        words += word

with open('3_words_pinyin.txt', 'w') as f2:
    for w1 in words:
        for w2 in words:
            for w3 in words:
	        f2.write(w1 + w2 + "." + w3 + '\n')
