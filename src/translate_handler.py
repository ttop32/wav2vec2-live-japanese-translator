from googletrans import Translator


class TranslateHandler:
    translator = Translator()

    langCodeDict={
        "None":"none",
        "Afrikaans":"af",
        "Albanian":"sq",
        "Amharic":"am",
        "Arabic":"ar",
        "Armenian":"hy",
        "Azerbaijani":"az",
        "Basque":"eu",
        "Belarusian":"be",
        "Bengali":"bn",
        "Bosnian":"bs",
        "Bulgarian":"bg",
        "Catalan":"ca",
        "Cebuano":"ceb",
        "Chichewa":"ny",
        "Chinese Simplified":"zh-cn",
        "Chinese Traditional":"zh-tw",
        "Corsican":"co",
        "Croatian":"hr",
        "Czech":"cs",
        "Danish":"da",
        "Dutch":"nl",
        "English":"en",
        "Esperanto":"eo",
        "Estonian":"et",
        "Filipino":"tl",
        "Finnish":"fi",
        "French":"fr",
        "Frisian":"fy",
        "Galician":"gl",
        "Georgian":"ka",
        "German":"de",
        "Greek":"el",
        "Gujarati":"gu",
        "Haitian Creole":"ht",
        "Hausa":"ha",
        "Hawaiian":"haw",
        "Hebrew":"iw",
        "Hindi":"hi",
        "Hmong":"hmn",
        "Hungarian":"hu",
        "Icelandic":"is",
        "Igbo":"ig",
        "Indonesian":"id",
        "Irish":"ga",
        "Italian":"it",
        "Japanese":"ja",
        "Javanese":"jw",
        "Kannada":"kn",
        "Kazakh":"kk",
        "Khmer":"km",
        "Korean":"ko",
        "Kurdish (Kurmanji)":"ku",
        "Kyrgyz":"ky",
        "Lao":"lo",
        "Latin":"la",
        "Latvian":"lv",
        "Lithuanian":"lt",
        "Luxembourgish":"lb",
        "Macedonian":"mk",
        "Malagasy":"mg",
        "Malay":"ms",
        "Malayalam":"ml",
        "Maltese":"mt",
        "Maori":"mi",
        "Marathi":"mr",
        "Mongolian":"mn",
        "Myanmar (Burmese)":"my",
        "Nepali":"ne",
        "Norwegian":"no",
        "Pashto":"ps",
        "Persian":"fa",
        "Polish":"pl",
        "Portuguese":"pt",
        "Punjabi":"pa",
        "Romanian":"ro",
        "Russian":"ru",
        "Samoan":"sm",
        "Scots Gaelic":"gd",
        "Serbian":"sr",
        "Sesotho":"st",
        "Shona":"sn",
        "Sindhi":"sd",
        "Sinhala":"si",
        "Slovak":"sk",
        "Slovenian":"sl",
        "Somali":"so",
        "Spanish":"es",
        "Sundanese":"su",
        "Swahili":"sw",
        "Swedish":"sv",
        "Tajik":"tg",
        "Tamil":"ta",
        "Telugu":"te",
        "Thai":"th",
        "Turkish":"tr",
        "Ukrainian":"uk",
        "Urdu":"ur",
        "Uyghur":"ug",
        "Uzbek":"uz",
        "Vietnamese":"vi",
        "Welsh":"cy",
        "Xhosa":"xh",
        "Yiddish":"yi",
        "Yoruba":"yo",
        "Zulu":"zu"
        }

    @classmethod
    def translate(cls, text,fromlang="auto",tolang="en"):
        if tolang=="none":
            return text
        return cls.translator.translate(text, src=fromlang, dest=tolang).text





# # https://github.com/ssut/py-googletrans/issues/268#issuecomment-850074462
#
# import requests
# from urllib.parse import urlencode
# import time
#
# class translateHandler:
#
#
#     def get_translation_url(sentance, tolanguage, fromlanguage='auto'):
#         """Return the url you should visit to get sentance translated to language tolanguage."""
#         query = {'client': 'gtx',
#                  'dt'    : 't',
#                  'sl'    : fromlanguage,
#                  'tl'    : tolanguage,
#                  'q'     : sentance}
#         url = 'https://translate.googleapis.com/translate_a/single?'+urlencode(query)
#         return url
#
#     def translate(sentance, tolang, fromlang='auto'):
#         """Use the power of sneeky tricks to do translation."""
#
#         MAGICHEADERS = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
#         }
#         TIMESLEEP = 3
#         # Get url from function, which uses urllib to generate proper query
#         url = get_translation_url(sentance, tolang, fromlang)
#         try:
#             # Make a get request to translate url with magic headers
#             # that make it work right cause google is smart and looks at that.
#             # Also, make request result be json so we can look at it easily
#             request_result = requests.get(url, headers=MAGICHEADERS).json()
#         except Exception as ex:
#             # If it broke somehow, try again
#             time.sleep(TIMESLEEP)
#             try:
#                 request_result = requests.get(url, headers=MAGICHEADERS).json()
#             except:
#                 return ""
#
#         # After we get the result, get the right field of the response and return that.
#         # If result field not in request result
#         def get_parts(lst):
#             usefull = []
#             for i in lst:
#                 if isinstance(i, list):
#                     usefull += get_parts(i)
#                 elif i:
#                     usefull.append(i)
#             return usefull
#         return get_parts(request_result)[0]




if __name__ == '__main__':
    text=TranslateHandler.translate("hello world",fromlang="auto",tolang="ko")
    print(text)
