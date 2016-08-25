using HtmlAgilityPack;

namespace CUHKOne.Controllers
{
  public class HTMLParser
  {
    public HtmlNodeCollection parser(string addr)
    {
      HtmlDocument document = new HtmlDocument();
      document.LoadHtml("http://cumassmail.itsc.cuhk.edu.hk/weekly/Digest/List/UG/20160812");
      HtmlNodeCollection collection = document.DocumentNode.SelectNodes("//*[contains(@class,'float')]");
      return collection;
    }
  }
}