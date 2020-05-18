import re

def caseFolding(data):
    lower = data.lower()
    return lower

def tokenizing(data,pemisah):
    token = data.split(pemisah)
    return token

def entity(list):
    ANIMAL = ["anjing", "kuda", "sapi", "bebek", "hiu", "penyu", "ikan", "kerbau", "cicak", "buaya", "katak",
              "burung", "ayam", "kucing", "ular", "bekicot", "siput", "kerbau", "kelinci", "kangguru", "lebah", "kelelawar", "lintah", "cacing"]
    BODY = ["rambut", "bulu", "sisik", "cangkang"]
    LOCATION = ["air", "darat"]
    FOOD = ["tumbuhan", "daging", "segalanya"]
    MOVE = ["berjalan", "melompat", "terbang", "berenang", "melata"]
    ORGAN = ["insang", "paru", "kulit", "trakea"]
    SEX = ["bertelur", "melahirkan"]
    listBaru = []
    for i in list:
        if i in ANIMAL:
            ner = "ANIMAL"
        elif i in BODY:
            ner = "BODY"
        elif i in LOCATION:
            ner = "LOCATION"
        elif i in FOOD:
            ner = "FOOD"
        elif i in MOVE:
            ner = "MOVE"
        elif i in ORGAN:
            ner = "ORGAN"
        elif i in SEX:
            ner = "SEX"
        else:
            ner = "O"
        listBaru += [(i,ner)]
    return listBaru

def sinonim(pertanyaan):
    listsinonim = open("sinonim pertanyaan.txt", "r+").read().split(" ")
    splitPertanyaan = pertanyaan.split(" ")
    for k in range(len(splitPertanyaan)):
        sudahGanti = False
        for i in range(len(listsinonim)):
            sinonim = listsinonim[i].split("-")
            for j in range(len(sinonim)):
                if (splitPertanyaan[k] == sinonim[j]):
                    splitPertanyaan[k] = sinonim[0]
                    sudahGanti = True
                    break
            if (sudahGanti):
                break
    pertanyaan = ""
    for i in range(len(splitPertanyaan)):
        pertanyaan += splitPertanyaan[i] + " "
    return pertanyaan

def penggolonganPertanyaan(token,tokenNER, casefolding,listBaru):
    katadefinisi = ["amfibi", "ovipar", "vivipar", "ovovivipar", "herbivora", "karnivora", "omnivora"]
    kondisi = False
    for kata in katadefinisi:
        if kata in token and "apa" in token:
            jawab = pertanyaanDefinisi(kata, casefolding)
            kondisi = True
    if kondisi != True:
        jawab = cariRelasi(listBaru, tokenNER)
    return jawab

def cariRelasi(SeluruhList,pertanyaan):
    listTanya = []
    listNER = []
    for kata in pertanyaan:
        tanya,tag = kata
        listTanya.append(tanya)
        listNER.append(tag)
    if "apa" in listTanya and "penutup" in listTanya and "ANIMAL" in listNER:
        indexNERHewan = listNER.index("ANIMAL")
        relasi = "BODY"
        jawab = searchAnswerNER(SeluruhList, relasi, "penutup", listTanya[indexNERHewan])
    elif "dimana" in listTanya and "hidup" in listTanya and "ANIMAL" in listNER:
        indexNERHewan = listNER.index("ANIMAL")
        relasi = "LOCATION"
        jawab = searchAnswerNER(SeluruhList, relasi, "hidup", listTanya[indexNERHewan])
    elif "apa" in listTanya and "makan" in listTanya and "ANIMAL" in listNER:
        indexNERHewan = listNER.index("ANIMAL")
        relasi = "FOOD"
        jawab = searchAnswerNER(SeluruhList, relasi, "makan", listTanya[indexNERHewan])
    elif "bagaimana" in listTanya and "bergerak" in listTanya and "ANIMAL" in listNER:
        indexNERHewan = listNER.index("ANIMAL")
        relasi = "MOVE"
        jawab = searchAnswerNER(SeluruhList, relasi, "bergerak", listTanya[indexNERHewan])
    elif "bagaimana" in listTanya and "bernafas" in listTanya and "ANIMAL" in listNER:
        indexNERHewan = listNER.index("ANIMAL")
        relasi = "ORGAN"
        jawab = searchAnswerNER(SeluruhList, relasi, "bernafas", listTanya[indexNERHewan])
    elif "bagaimana" in listTanya and "berkembang" in listTanya and "ANIMAL" in listNER:
        indexNERHewan = listNER.index("ANIMAL")
        relasi = "SEX"
        jawab = searchAnswerNER(SeluruhList, relasi, "berkembang", listTanya[indexNERHewan])
    elif "siapa" in listTanya:
        jawab = pertanyaanContoh(listTanya,listNER)
    return jawab

def searchAnswerNER(SeluruhList,relasi,kataPenting,hewan):
    jawaban = []
    skor = []
    for list in SeluruhList:
        listKata = []
        listNER = []
        for kata in list:
            unpackKata, unpackNER = kata
            listKata.append(unpackKata)
            listNER.append(unpackNER)
        if kataPenting in listKata and hewan in listKata:
            jawaban.append(listKata[listNER.index(relasi)])
            skor.append(3)
        elif kataPenting in listKata and relasi in listNER:
            jawaban.append(listKata[listNER.index(relasi)])
            skor.append(2)
        elif hewan in listKata and relasi in listNER:
            jawaban.append(listKata[listNER.index(relasi)])
            skor.append(1)
    return jawaban[skor.index(max(skor))]

def pertanyaanDefinisi(hurufCari,doc):
    regex = r"[a-z].*%s" % (hurufCari)
    jawaban = re.findall(regex, doc)
    return(re.sub(r"\(.*", "", jawaban[0]))

def pertanyaanContoh(tanya,ner):
    corpus_raw = open("korpus.txt", 'r')
    fileCorpus = corpus_raw.read()
    hasil_caseFolding = caseFolding(fileCorpus)
    relasi =""
    NER = ""
    listRelasi = ["hidup", "penutup", "makan", "bergerak", "bernafas", "berkembang"]
    for kata in listRelasi:
        if kata in tanya:
            relasi = kata
    for kata in ner:
        if kata != "O":
            NER = tanya[ner.index(kata)]
    if(ner.count("LOCATION")==2):
        NER = "amfibi"
    elif(ner.count("SEX")==2):
        NER = "ovovivipar"
    regex = r"contoh.*%s.*%s.*" % (relasi,NER)
    kalimatJawaban = re.findall(regex, hasil_caseFolding)
    jawaban = re.sub(r"\w.*: ","",kalimatJawaban[0])
    return jawaban

def RUN():
    corpus_raw = open("korpus.txt", 'r')
    fileCorpus = corpus_raw.read()
    hasil_caseFolding = caseFolding(fileCorpus)
    hasil_Tokenizing = tokenizing(hasil_caseFolding,"\n")
    listBaru = []
    for i in range(len(hasil_Tokenizing)):
        ListTerbaru = entity(re.findall(r"[a-z0-9]+", hasil_Tokenizing[i]))
        listBaru.append(ListTerbaru)
    while True:
        question = input("Masukkan pertanyaan : ")
        pertanyaan = sinonim(question)
        pertanyaan_caseFolding = caseFolding(pertanyaan)
        pertanyaan_tokenizing = tokenizing(pertanyaan_caseFolding," ")
        pertanyaanNER = entity(pertanyaan_tokenizing)
        jawab = penggolonganPertanyaan(pertanyaan_tokenizing,pertanyaanNER, hasil_caseFolding,listBaru)
        print(jawab)

if __name__ == '__main__':
    RUN()