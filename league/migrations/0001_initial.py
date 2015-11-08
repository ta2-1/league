# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'League'
        db.create_table('league_league', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('league', ['League'])

        # Adding model 'LeagueCompetitor'
        db.create_table('league_leaguecompetitor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competitor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rating.Competitor'])),
            ('league', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['league.League'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('league', ['LeagueCompetitor'])

        # Adding model 'Game'
        db.create_table('league_game', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='home_game_set', to=orm['rating.Competitor'])),
            ('player2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='guest_game_set', to=orm['rating.Competitor'])),
            ('start_datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rating.Location'])),
            ('result1', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('result2', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('league', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['league.League'])),
        ))
        db.send_create_signal('league', ['Game'])

        # Adding model 'Rating'
        db.create_table('league_rating', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('league', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['league.League'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['league.Game'], null=True, blank=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('comment', self.gf('django.db.models.fields.TextField')()),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rating.Competitor'])),
            ('delta', self.gf('django.db.models.fields.FloatField')()),
            ('rating_before', self.gf('django.db.models.fields.FloatField')()),
            ('rating_after', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('league', ['Rating'])


    def backwards(self, orm):
        
        # Deleting model 'League'
        db.delete_table('league_league')

        # Deleting model 'LeagueCompetitor'
        db.delete_table('league_leaguecompetitor')

        # Deleting model 'Game'
        db.delete_table('league_game')

        # Deleting model 'Rating'
        db.delete_table('league_rating')


    models = {
        'league.game': {
            'Meta': {'object_name': 'Game'},
            'end_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'league': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['league.League']"}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rating.Location']"}),
            'player1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'home_game_set'", 'to': "orm['rating.Competitor']"}),
            'player2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'guest_game_set'", 'to': "orm['rating.Competitor']"}),
            'result1': ('django.db.models.fields.SmallIntegerField', [], {}),
            'result2': ('django.db.models.fields.SmallIntegerField', [], {}),
            'start_datetime': ('django.db.models.fields.DateTimeField', [], {})
        },
        'league.league': {
            'Meta': {'object_name': 'League'},
            'competitors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'leagues'", 'symmetrical': 'False', 'through': "orm['league.LeagueCompetitor']", 'to': "orm['rating.Competitor']"}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'league.leaguecompetitor': {
            'Meta': {'object_name': 'LeagueCompetitor'},
            'competitor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rating.Competitor']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'league': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['league.League']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'league.rating': {
            'Meta': {'object_name': 'Rating'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'delta': ('django.db.models.fields.FloatField', [], {}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['league.Game']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'league': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['league.League']"}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rating.Competitor']"}),
            'rating_after': ('django.db.models.fields.FloatField', [], {}),
            'rating_before': ('django.db.models.fields.FloatField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        'rating.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        'rating.competitor': {
            'Meta': {'object_name': 'Competitor'},
            'birthDate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rating.Category']"}),
            'firstName': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastName': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'rating.location': {
            'Meta': {'object_name': 'Location'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        }
    }

    complete_apps = ['league']
