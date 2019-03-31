require 'pry'
require 'stemmify'

class Lemmatizator
  def call
    binding.pry
    puts words
  end

  private

  def read_stop_words
    result = []
    File.open("/Users/ismglv/dev/info-search-homeworks/stop-words.txt", "r") do |f|
      f.each_line do |line|
        result << line.strip
      end
    end

    result
  end

  def stop_words
    @stop_words ||= read_stop_words
  end

  def all_words
    Article.all.map{ |article| article.content.downcase.split(/[^[[:word:]]]+/) }.flatten
  end

  def words
    @words ||= all_words.select { |word| word.stem if !stop_words.include?(word.strip) }
  end
end
