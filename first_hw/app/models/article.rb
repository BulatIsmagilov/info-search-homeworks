class Article < ActiveRecord::Base
  belongs_to :student, class_name: "Student",
    foreign_key: "student_uuid"
end
