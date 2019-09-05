from ezreq import EzReq as Http


def main():
  http = Http("https://music.163.com")
  print(
      http.get("").text,
      http.get("//baidu.com").text,
      http.get("/robots.txt").text,
      http.get("?page=1").text
  )


main()
