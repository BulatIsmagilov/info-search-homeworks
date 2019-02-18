require 'nokogiri'
require 'restclient'
require 'pry'

class Crawler
  URLS = ["https://habr.com/ru", "https://habr.com/ru/page2"]
  TITLES_CSS = ".post__title_link"
  TITLE_CSS = ".post__title-text"
  CONTENT_CSS = ".post__text"
  TAGS_CSS = ".post__tag"

  def call
    titles_links.each do |link|
      parse_article(link)
    end
  end

  private

  def titles_links
    result = []
    URLS.each do |url|
      page = Nokogiri::HTML(RestClient.get(url))
      result += page.css(".post__title_link").map { |title| title.values.first }
    end

    result
  end

  def parse_article(url)
    @page = Nokogiri::HTML(RestClient.get(url))

    Article.create(title: title, keywords: keywords, content: content, url: url, student_uuid: Student.first.uuid)
  end

  def keywords
    @page.css(".post__tag").map { |tag| tag.text }.join(" ")
  end

  def title
    @page.css(".post__title-text").text
  end

  def content
    @page.css(".post__text").text
  end
end
