class CreateArticles < ActiveRecord::Migration[5.2]
  def change
    create_table :students do |t|
      t.string :name
      t.string :surname
      t.string :uuid
      t.string :group
    end

    create_table :articles do |t|
      t.string :title
      t.string :keywords
      t.string :content
      t.string :url
      t.string :student_uuid
    end
  end
end
