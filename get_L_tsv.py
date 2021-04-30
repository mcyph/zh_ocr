# -*- coding: utf-8 -*-
import re
import codecs
import thread
from glob import glob
from consts import base_dir
import hashlib

from copy import deepcopy
#import sqlitedict
from multi_translit.translit.icu import translit


def sort_human(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)


DReplace = {
    u'面钓': u'面的',
    u'汊': u'汉',
    u'〈所': u'其所',
    u"'": u'·',
    u'm级': u'10级',
    u'z级': u'2级',
    u'′Z周': u'2周',
    u'′': u'一',
    u'各船': u'各册',
    u'敦学': u'教学',
    u'盲教': u'意教',
    u'叉有': u'又有',
    u'抬级': u'设计',
    u'宇短': u'字短',
    u'时阆': u'时阆',
    u'元可': u'无可',
    u'不趋': u'不起',
    u'夕卜': u'外',
    u'一趋': u'一起',
    u'妤': u'好',
    u'对予': u'对于',
    u'予': u'子',
    u'戌': u'成',
    u'戍': u'成',
    u'耍': u'要',
    u'昱': u'里',
    u'亭受': u'享受',
    u'亭': u'事',
    u'夭': u'天',
    u'她铁': u'地铁',
    u'采': u'来',
    u'戎': u'我',
    u'柱': u'往',
    u'昏矛': u'婚礼',
    u'鳌埋': u'整理',
    u'埋': u'理',
    u'孝卜': u'补',
    u'耒': u'来',
    u'腈': u'睛',
    u'期眼': u'期限',
    u'亨': u'事',
    u'郾': u'圈',
    u'分子': u'分手',
    u'惰': u'情',
    u'艮孝': u'很',
    u'祚': u'在',
    u'纤‖': u'细',
    u'仝': u'全',
    u'来述': u'来过',
    u'堵丰': u'堵车',
    u'交车': u'交车',
    u'辆丰': u'辆车',
    u'丰厢': u'车厢',
    u'丰竟': u'毕竟',
    u'1故': u'做',
    u'故到': u'做',
    u'故事': u'故事',
    u'葉故': u'做',
    u'桌羞': u'更美',
    u'幔': u'慢',
    u'元隔干里': u'元隔千里',
    u'尊赦': u'尊敬',
    u'淅': u'渐',
    u'儡然': u'偶然',
    u'桌实': u'真实',
    u'敖学': u'教学',
    u'霄': u'需'
}


class Book:
    def __init__(self, book_name):
        self.book_name = book_name
        self.exception_lock = thread.allocate_lock()

        exc_file_path = '%s/%s/exceptions.json' % (
            base_dir,
            book_name.replace('_', ' ')
        )
        self.exception_file = open(exc_file_path, "ab+")

    def get_L_tsv(self):
        LRtn = []
        tsv_dir = '%s/%s/tsv' % (base_dir, self.book_name.replace('_', ' '))

        for path in sort_human(glob('%s/*.tsv' % tsv_dir)):
            # TODO: PROPERLY SORT ME!!! ==========================================================
            print path
            LRtn.append((
                path.split('/')[-1].split('.')[0],
                self._get_L_tsv(path)
            ))

        return LRtn

    def _get_L_tsv(self, path):
        LRtn = []
        DExc = self.get_D_exceptions()

        with codecs.open(path, 'rb', 'utf-8') as f:
            for x, line in enumerate(f):
                if not line.strip() or line.count('\t') < 11:
                    continue
                elif not x:
                    continue
                LLine = line.split('\t')

                D = {}
                D['level'] = int(LLine[0])
                D['page_num'] = int(LLine[1])
                D['block_num'] = int(LLine[2])
                D['par_num'] = int(LLine[3])
                D['line_num'] = int(LLine[4])
                D['word_num'] = int(LLine[5])
                D['left'] = int(LLine[6])
                D['top'] = int(LLine[7])
                D['width'] = int(LLine[8])
                D['height'] = int(LLine[9])
                D['confidence'] = int(LLine[10])
                D['text'] = '\t'.join(LLine[11:]).strip()

                D['hash'] = hashlib.sha384(line.strip().encode('utf-8')).hexdigest()
                D['orig_text'] = D['text']

                if D['orig_text'] in DExc:
                    # Use the previously stored override value
                    # (These are all assumed traditional Chinese)
                    D['text'] = D['text_trad'] = DExc[D['orig_text']]
                else:
                    # Use the tesseract value, trying to clean up common mistakes

                    # Filter out mostly junk latin chars
                    zh_chars = re.findall(ur'[\u4e00-\u9fff]+', D['text'])
                    if not zh_chars or len(''.join(zh_chars)) <= (len(D['text'].strip())-1)/2.0:
                        continue

                    if D['text'][-1] in u'oDgucna~q':
                        D['text'] = D['text'][:-1]+u'。' # HACK!
                    elif D['text'][-1] in u'yv′\'`':
                        D['text'] = D['text'][:-1] + u','

                    for k, v in sorted(DReplace.items(), key=lambda x: -len(x[0])):
                        D['text'] = D['text'].replace(k, v)

                    D['text_trad'] = translit('zh', 'zh_Hant', D['text'])

                LRtn.append(D)

        return LRtn

    def add_exception(self, hash_, orig_text, new_text):
        def process(s):
            s = s.replace('\r', '')
            s = s.replace('\n', '')
            s = s.replace('\t', '')
            return s

        with self.exception_lock:
            # Move to end of file for append
            self.exception_file.seek(0, 2)
            self.exception_file.write((
                    '%s\t%s\t%s\n' % (hash_, process(orig_text), process(new_text))
            ).encode('utf-8', 'replace'))
            self.exception_file.flush()

    def get_D_exceptions(self):
        D = {}

        with self.exception_lock:
            # Move to start of file
            self.exception_file.seek(0)

            for line in self.exception_file:
                if not line.strip():
                    continue

                key, orig_text, new_text = line.split('\t')
                orig_text = orig_text.decode('utf-8', 'replace')
                new_text = new_text.decode('utf-8', 'replace')
                D[orig_text] = new_text

            # Move to end of file
            self.exception_file.seek(0, 2)
        return D


if __name__ == '__main__':
    name = '10 level chinese 7 intensive'
    from pprint import pprint
    pprint(get_L_tsv(name))
