# -*- coding: utf-8 -*-
import os
import flaskr
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        """Before each test, set up a blank database"""
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.config['TESTING'] = True
        self.app = flaskr.app.test_client()
        flaskr.init_db()

    def tearDown(self):
        """Get rid of the database again after each test."""
        os.close(self.db_fd)

    def login(self, username, password):
        return self.app.post('/login', data = dict(username = username, 
                        password = password ), follow_redirects = True)
        
    def add_user(self, username, password):
        return self.app.post('/add-user', data = dict(username = username,
                        password = password ), follow_redirects = True)
    
    def add_entry(self, title, text):
        return self.app.post('/add', data = dict(title = title, text = text ),
                        follow_redirects = True)
        
    def add_podpiska(self, polzovatel, dryg):
        return self.app.post('/podpiska', data = dict(polzovatel = polzovatel,
                        dryg = dryg ), follow_redirects = True)

    def zamena_login(self, password):
        return self.app.post('/zamena_login', data = dict(password = password),
                        follow_redirects = True)    
    
    def repost(self, id_post, user):
        return self.app.get(('/repost-post/' + str(id_post) + ' ' + str(user) +
                        ' '), follow_redirects = True)
    
    def add_like(self, id_posta, kol_laikov, id_polzovat):
        return self.app.get('/add-like/' + ' ' + str(id_posta) + ' ' + 
                        str(kol_laikov) + ' ' + str(id_polzovat) + 
                        ' ', follow_redirects = True)       
   
    def dizlake(self, id_posta, kol_laikov, id_polzovat):
        return self.app.get('/dizlake/' + ' ' + str(id_posta) + ' ' + 
                        str(kol_laikov) + ' ' + str(id_polzovat) + 
                        ' ', follow_redirects = True)

    def add_dryg(self, polzovatel, dryg, id_podpicika):
        return self.app.get('/add-dryg/'+str(polzovatel)+ ' ' + str(dryg) + 
                        ' ' + str(id_podpicika), follow_redirects = True)
 
    def dell_dryg(self, polzovatel, id_podpicika):
        return self.app.get('/dell-dryg/'+str(polzovatel)+ '  ' + 
                        str(id_podpicika), follow_redirects=True)

    def dell_post(self, id_posta):
        return self.app.post('/dell-post/ '+ str(id_posta),
                        follow_redirects = True)

    def show_like(self, id_posta):
        return self.app.get(('/show-like/'+str(id_posta)+' '),
                        follow_redirects = True)

    def profil(self, name):
        return self.app.get(('/profil ' + str(name) + ' '), follow_redirects = True)
        
    def top_10(self):
        return self.app.get('/top10', follow_redirects = True)

    def top_10_7(self):
        return self.app.get('/top10-7', follow_redirects = True)
        
    def logout(self):
        return self.app.get('/logout', follow_redirects = True)

    # testing functions
    def test_add_dryg(self):
        """Добавляем подписчика в друзья"""
        # друг
        dryg = '123'
        password = '1'
        rv = self.add_user(dryg, password)
        assert b'Dobro pozalovat ' + dryg in rv.data
        rv = self.logout()
        # пользователь
        polzovatel = '12345'
        password = '1'
        rv = self.add_user(polzovatel, password)
        assert b'Dobro pozalovat ' + polzovatel in rv.data
        # добавляемся в др
        rv = self.add_podpiska(polzovatel, dryg)
        assert b'Vi podpisalis na polzovatelya' in rv.data
        rv = self.logout()
        rv = self.login(dryg, password)
        assert b'Dobro pozalovat ' + dryg in rv.data
        rv = self.add_dryg(polzovatel, dryg, 1)
        assert b'Dobavlen v dr' in rv.data
   
    def test_add_dryg_no_auth(self):
        """Добавляем подписчика в друзья"""
        # друг
        dryg = '123'
        password = '1'
        rv = self.add_user(dryg, password)
        assert b'Dobro pozalovat ' + dryg in rv.data
        rv = self.logout()
        # пользователь
        polzovatel = '12345'
        password = '1'
        rv = self.add_user(polzovatel, password)
        assert b'Dobro pozalovat ' + polzovatel in rv.data
        # добавляемся в др
        rv = self.add_podpiska(polzovatel, dryg)
        assert b'Vi podpisalis na polzovatelya' in rv.data
        rv = self.logout()      
        rv = self.add_dryg(polzovatel, dryg, 1)
        assert b'401 Unauthorized' in rv.data
        
    def test_dell_dryg(self):
        """Удаляем друзей из списка друзей"""
        # друг
        dryg = '123'
        password = '1'
        rv = self.add_user(dryg, password)
        assert b'Dobro pozalovat ' + dryg in rv.data
        rv = self.logout()
        # пользователь
        polzovatel = '12345'
        password = '1'
        rv = self.add_user(polzovatel, password)
        assert b'Dobro pozalovat ' + polzovatel in rv.data
        # добавляемся в др
        rv = self.add_podpiska(polzovatel, dryg)
        assert b'Vi podpisalis na polzovatelya' in rv.data
        rv = self.logout()
        rv = self.login(dryg, password)
        assert b'Dobro pozalovat ' + dryg in rv.data
        rv = self.add_dryg(polzovatel, dryg, 1)
        assert b'Dobavlen v dr' in rv.data
        rv = self.dell_dryg(dryg, 1)
        assert b'Ydalen iz dr' in rv.data

    def test_dell_dryg_no_auth(self):
        """Удаляем друзей из списка друзей не авторизованным"""
        # друг
        dryg = '123'
        password = '1'
        rv = self.add_user(dryg, password)
        assert b'Dobro pozalovat ' + dryg in rv.data
        rv = self.logout()
        # пользователь
        polzovatel = '12345'
        password = '1'
        rv = self.add_user(polzovatel, password)
        assert b'Dobro pozalovat ' + polzovatel in rv.data
        # добавляемся в др
        rv = self.add_podpiska(polzovatel, dryg)
        assert b'Vi podpisalis na polzovatelya' in rv.data
        rv = self.logout()
        rv = self.login(dryg, password)
        assert b'Dobro pozalovat ' + dryg in rv.data
        rv = self.add_dryg(polzovatel, dryg, 1)
        assert b'Dobavlen v dr' in rv.data
        rv = self.logout()  
        rv = self.dell_dryg(dryg, 1)    
        assert b'401 Unauthorized' in rv.data
        
    def test_add_user(self):
        """Регистрация пользователя"""
        username = '123'
        password = '1'
        rv = self.add_user(username, password)
        assert b'Dobro pozalovat ' + username in rv.data

    def test_login(self):
        """Авторизация пользователя"""
        username = '123'
        password = '1'
        rv = self.add_user(username, password)
        assert b'Dobro pozalovat ' + username in rv.data
        rv = self.logout()
        rv = self.login(username, password)
        assert b'Dobro pozalovat ' + username in rv.data
    
    def test_no_login(self):
        """Не удачный ввод данных для авторизации пользователя"""
        username = '123'
        password = '1'
        rv = self.add_user(username, password)
        assert b'Dobro pozalovat ' + username in rv.data
        rv = self.logout()
        rv = self.login(username, password + '12')
        assert b'Osibka vvoda danih' in rv.data     
    
    def test_top_10(self):
        """ Топ 10 """
        rv = self.top_10()
        assert b'Top 10' in rv.data

    def test_top_10_7(self):
        """ Топ 10 за неделю """
        rv = self.top_10_7()
        assert b'Top 10' in rv.data
        
    def test_profil(self):
        """ Профиль пользователя """
        username = '123'
        password = '1'
        rv = self.add_user(username, password)
        assert b'Dobro pozalovat ' + username in rv.data
        rv = self.profil(username)
        assert b'Профиль пользователя' in rv.data
    
    def test_zamena_login(self):
        """ Замена пароля пользователя """
        username = '123'
        password = '1'
        rv = self.add_user(username, password)
        assert b'Dobro pozalovat ' + username in rv.data
        rv = self.zamena_login('1234')
        assert b'danie sohraneni' in rv.data        

    def test_zamena_login_no_auth(self):
        """ Замена пароля пользователя """
        username = '123'
        password = '1'
        rv = self.add_user(username, password)
        assert b'Dobro pozalovat ' + username in rv.data
        rv = self.logout()      
        rv = self.zamena_login('1234')
        assert b'401 Unauthorized' in rv.data  
        
    def test_show_like(self):
        """ Просмотр лайков поста """
        username = '123'
        password = '1'
        rv = self.add_user(username, password)
        assert b'Dobro pozalovat ' + username in rv.data
        rv = self.add_entry('123', 'ASDASDASDASD')
        assert b'New entry was successfully posted' in rv.data  
        rv = self.show_like('1')
        assert b'Prosmotr laikov' in rv.data
 
    def test_show_like_no_auth(self):
        """ Просмотр лайков поста """
        username = '123'
        password = '1'
        rv = self.add_user(username, password)
        assert b'Dobro pozalovat ' + username in rv.data
        rv = self.add_entry('123', 'ASDASDASDASD')
        assert b'New entry was successfully posted' in rv.data
        rv = self.logout()      
        rv = self.show_like('1')
        assert b'401 Unauthorized' in rv.data
        
    def test_add_user_1(self):
        """Регистрация пользователя дважды"""
        username = '123'
        password = '1'
        rv = self.add_user(username, password)
        rv = self.add_user(username, password)
        assert b'takoi login yze est' in rv.data

    def test_add_entry(self):
        """Добавляем пост """
        username = '123'
        password = '1'
        rv = self.add_user(username, password)
        assert b'Dobro pozalovat ' + username in rv.data
        rv = self.add_entry('123', '123123')
        assert b'New entry was successfully posted' in rv.data
    
    def test_add_entry_no_auth(self):
        """Добавляем пост не авторизованным"""
        username = '123'
        password = '1'
        rv = self.add_user(username, password)
        assert b'Dobro pozalovat ' + username in rv.data
        rv = self.logout()
        rv = self.add_entry('123', '123123')
        assert b'401 Unauthorized' in rv.data   
    
    def test_dell_post(self):
        """Удаляем существующий пост"""
        username = '123'
        password = '1'
        rv = self.add_user(username, password)
        assert b'Dobro pozalovat ' + username in rv.data
        rv = self.add_entry('123','ASDASDASDASDASDASDASD')
        assert b'New entry was successfully posted' in rv.data  
        rv = self.dell_post(1)
        assert b'Post ydalen' in rv.data        

    def test_dell_post_no_auth(self):
        """Удаляем существующий пост неавторизованным"""
        username = '123'
        password = '1'
        rv = self.add_user(username, password)
        assert b'Dobro pozalovat ' + username in rv.data
        rv = self.add_entry('123','ASDASDASDASDASDASDASD')
        assert b'New entry was successfully posted' in rv.data
        rv = self.logout()      
        rv = self.dell_post(1)
        assert b'401 Unauthorized' in rv.data
        
    def test_dell_null_post_(self):
        """Удаляем несуществующий пост"""
        username = '123'
        password = '1'
        rv = self.add_user(username, password)
        assert b'Dobro pozalovat '+ username in rv.data
        rv = self.dell_post(11)
        assert b'Takogo posta net' in rv.data   
        
    def test_logout(self):
        """Выходим из учетной записи"""
        username = '123'
        password = '1'
        rv = self.add_user(username, password)
        assert b'Dobro pozalovat ' + username in rv.data
        rv = self.logout()
        assert b'You were logged out' in rv.data

    def test_podpiska(self):
        """Подписываемся на 1 - 2 раза"""
        # друг
        dryg = '123'
        password = '1'
        rv = self.add_user(dryg, password)
        assert b'Dobro pozalovat ' + dryg in rv.data
        rv = self.logout()
        # пользователь
        polzovatel = '12345'
        password = '1'
        rv = self.add_user(polzovatel, password)
        assert b'Dobro pozalovat ' + polzovatel in rv.data
        # добавляемся в др
        rv = self.add_podpiska(polzovatel, dryg)
        assert b'Vi podpisalis na polzovatelya' in rv.data
        rv = self.add_podpiska(polzovatel, dryg)
        assert b'Vi yze v podpiskah' in rv.data
   
    def test_podpiska_no_auth(self):
        """Подписываемся на пользователя, не авторизованным"""
        # друг
        dryg = '123'
        password = '1'
        rv = self.add_user(dryg, password)
        assert b'Dobro pozalovat ' + dryg in rv.data
        rv = self.logout()
        # пользователь
        polzovatel = '12345'
        password = '1'
        rv = self.add_user(polzovatel, password)
        assert b'Dobro pozalovat ' + polzovatel in rv.data
        rv = self.logout()
        # Подписываемся на пользователя в др
        rv = self.add_podpiska(polzovatel, dryg)
        assert b'401 Unauthorized' in rv.data
        
    def test_repost(self):
        """Репост сообщения"""
        dryg = '123'
        password = '1'
        rv = self.add_user(dryg, password)
        assert b'Dobro pozalovat ' + dryg in rv.data
        rv = self.add_entry('123', '123123')
        assert b'New entry was successfully posted' in rv.data
        rv = self.logout()
        # пользователь
        polzovatel = '12345'
        password = '1'
        rv = self.add_user(polzovatel, password)
        assert b'Dobro pozalovat ' + polzovatel in rv.data
        # репост сообщения
        rv = self.repost(1, polzovatel)
        assert b'Post dobavlen v vasy lenty' in rv.data

    def test_repost_no_auth(self):
        """Репост сообщения не авторизованным"""
        dryg = '123'
        password = '1'
        rv = self.add_user(dryg, password)
        assert b'Dobro pozalovat ' + dryg in rv.data
        rv = self.add_entry('123', '123123')
        assert b'New entry was successfully posted' in rv.data
        rv = self.logout()
        # пользователь
        polzovatel = '12345'
        password = '1'
        rv = self.add_user(polzovatel, password)
        assert b'Dobro pozalovat ' + polzovatel in rv.data
        # репост сообщения
        rv = self.logout()
        rv = self.repost(1, polzovatel)
        assert b'401 Unauthorized' in rv.data
        
    def test_null_repost(self):
        """Добавление не существующего поста """
        dryg = '123'
        password = '1'
        rv = self.add_user(dryg, password)
        assert b'Dobro pozalovat ' + dryg in rv.data
        rv = self.add_entry('123', '123123')
        assert b'New entry was successfully posted' in rv.data
        rv = self.logout()
        # пользователь
        polzovatel = '12345'
        password = '1'
        rv = self.add_user(polzovatel, password)
        assert b'Dobro pozalovat ' + polzovatel in rv.data
        # репост не существующего сообщения
        rv = self.repost(2, polzovatel)
        assert b'Takogo posta net' in rv.data

    def test_add_like(self):
        """Ставим лайк на пост """
        dryg = '123'
        password = '1'
        rv = self.add_user(dryg, password)
        assert b'Dobro pozalovat ' + dryg in rv.data
        rv = self.add_entry('123', '123123')
        assert b'New entry was successfully posted' in rv.data
        # ставил like
        rv = self.add_like('1', '0', dryg)
        assert b'like dobavlen' in rv.data
        
    def test_add_like_no_auth(self):
        """Ставим лайк на пост не авторизованным"""
        dryg = '123'
        password = '1'
        rv = self.add_user(dryg, password)
        assert b'Dobro pozalovat ' + dryg in rv.data
        rv = self.add_entry('123', '123123')
        assert b'New entry was successfully posted' in rv.data
        rv = self.logout()
        # ставил like
        rv = self.add_like('1', '0', dryg)
        assert b'401 Unauthorized' in rv.data 
            
    def test_add_like_2(self):
        """Ставим 2 раза лайк на пост """
        dryg = '123'
        password = '1'
        rv = self.add_user(dryg, password)
        assert b'Dobro pozalovat ' + dryg in rv.data
        rv = self.add_entry('123', '123123')
        assert b'New entry was successfully posted' in rv.data
        # ставил like
        rv = self.add_like('1', '0', dryg)
        assert b'like dobavlen' in rv.data  
        rv = self.add_like('1', '1', dryg)
        assert b'Vi yze stavili like' in rv.data    

    def test_dizlake(self):
        """Ставим дизлайк на пост """
        dryg = '123'
        password = '1'
        rv = self.add_user(dryg, password)
        assert b'Dobro pozalovat ' + dryg in rv.data
        rv = self.add_entry('123', '123123')
        assert b'New entry was successfully posted' in rv.data
        rv = self.dizlake('1', '0', dryg)
        assert b'dizlake dobavlen' in rv.data
   
    def test_dizlake_2(self):
        """Ставим 2 раза дизлайк на пост """
        dryg = '123'
        password = '1'
        rv = self.add_user(dryg, password)
        assert b'Dobro pozalovat ' + dryg in rv.data
        rv = self.add_entry('123', '123123')
        assert b'New entry was successfully posted' in rv.data
        rv = self.dizlake('1', '0', dryg)
        assert b'dizlake dobavlen' in rv.data   
        rv = self.dizlake('1', '1', dryg)
        assert b'Vi yze stavili dizlake' in rv.data
   
    def test_dizlake_no_auth(self):
        """Ставим дизлайк на пост не авторизованным """
        dryg = '123'
        password = '1'
        rv = self.add_user(dryg, password)
        assert b'Dobro pozalovat ' + dryg in rv.data
        rv = self.add_entry('123', '123123')
        assert b'New entry was successfully posted' in rv.data
        rv = self.logout()
        rv = self.dizlake('1', '0', dryg)
        assert b'401 Unauthorized' in rv.data
        
if __name__ == '__main__':
    unittest.main()
