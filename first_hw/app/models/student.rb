class Student < ActiveRecord::Base
  has_many :articles
end
