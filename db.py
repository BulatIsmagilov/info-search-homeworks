#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import itertools
import psycopg2
import psycopg2.extras

import config

class DB:
    def __init__(self):
        """ Class constructor """
        conn_string = f"host={config.db_host} dbname={config.db_name} user={config.db_user} password={config.db_password}"
        self.conn = psycopg2.connect(conn_string)

    def disconnect(self):
        if self.conn is not None:
            self.conn.close()

    def get_articles(self):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT id, content from articles;")
        msg_tuples = cursor.fetchall()
        return msg_tuples

    def insert_porter(self, uuid, word, article_id):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO words_porter(id, term, article_id) VALUES(%s, %s, %s)", (uuid, word, article_id))
        self.conn.commit()

    def insert_my_stem(self, uuid, word, article_id):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO words_mystem(id, term, article_id) VALUES(%s, %s, %s)", (uuid, word, article_id))
        self.conn.commit()

    def insert_users(self, users_list):
        """ insert multiple users into table """
        sql = "INSERT INTO users(username) VALUES %s ON CONFLICT DO NOTHING"
        try:
            cursor = self.conn.cursor()
            psycopg2.extras.execute_values(
                cursor, sql, users_list, template=None, page_size=10
            )
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("PSYCOPG ERROR DURING USER INSERT: ", error)

    def insert_attachments(self, attachments_list):
        """ insert multiple attachments into table """
        sql = "INSERT INTO attachments(chat_id, message_id, tg_msg_id, file_link, status) VALUES %s"
        try:
            cursor = self.conn.cursor()
            psycopg2.extras.execute_values(
                cursor, sql, attachments_list, template=None, page_size=10
            )
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("PSYCOPG ERROR DURING ATTACHMENTS INSERT: ", error)

    def get_messages(self, chat_id, tg_msg_ids):
        cursor = self.conn.cursor()
        sql = "SELECT id, tg_msg_id, file_link from messages WHERE chat_id = %s AND tg_msg_id IN %s"
        cursor.execute(sql, (chat_id, tuple(tg_msg_ids)))
        msg_tuples = cursor.fetchall()
        return msg_tuples

    def set_last_saved_msg_id(self, chat_id, msg_id):
        """ update last saved msg id"""
        sql = "UPDATE chats SET last_saved_msg_id=%s, updated_at=(now() at time zone 'utc') WHERE chats.id=%s"
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (msg_id, chat_id))
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("PSYCOPG UPDATE LAST MESSAGE ID ERROR ", error)

    def local_rtmids(self, chat_id, rtm_ids):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT id, tg_msg_id FROM messages WHERE chat_id={chat_id} AND tg_msg_id IN ({', '.join(rtm_ids)})")
        result = cursor.fetchall()
        return result if result else []

    def set_local_response_message_id(self, lrm_id, chat_id, m_id):
        """ set local response message id """
        sql = "UPDATE messages SET local_respond_to_msg_id=%s WHERE chat_id=%s AND messages.respond_to_msg_id=%s"
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (lrm_id, chat_id, m_id))
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("PSYCOPG UPDATE MESSAGE RESPONSE ERROR ", error)

    def get_undowlnoad_attachments(self):
        """ get attachments which does not dowloaded """
        sql = "select attachments.id, attachments.message_id, attachments.tg_msg_id, chats.tg_link from attachments INNER JOIN chats on chats.id = attachments.chat_id where attachments.status = 0;"
        cursor = self.conn.cursor()
        cursor.execute(sql)
        attachments_tuples = cursor.fetchall()
        return attachments_tuples

    def update_attachment(self, link, attachment_id):
        sql = "UPDATE attachments SET status=1, file_link=%s WHERE id=%s"
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (link, attachment_id))
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("PSYCOPG UPDATE ATTACHMENT ERROR ", error)

    def delete_attachment(self, attachment_id):
        sql = "DELETE FROM attachments WHERE id=%s"
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (attachment_id,))
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("PSYCOPG DELETE ATTACHMENT ERROR ", error)

    def delete_message(self, message_id):
        sql = "DELETE FROM messages WHERE id=%s"
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (message_id,))
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("PSYCOPG DELETE MESSAGE ERROR ", error)
