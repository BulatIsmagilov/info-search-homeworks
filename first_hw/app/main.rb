require 'active_record'
require_relative './models/student'
require_relative './models/article'
require_relative './services/crawler'
require_relative './services/lemmatizator'
require 'pry'

def db_configuration
  db_configuration_file = File.join(File.expand_path('..', __FILE__), '..', 'db', 'config.yml')
  YAML.load(File.read(db_configuration_file))
end

ActiveRecord::Base.establish_connection(db_configuration["development"])
binding.pry

# Crawler.new.()
Lemmatizator.new.()

