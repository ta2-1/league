# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration, DataMigration
from django.db import models
from league.models import League

class Migration(DataMigration):

    def forwards(self, orm):
        # Adding field 'LeagueCompetitor.tournament_category'
        db.add_column('league_leaguecompetitor', 'tournament_category',
                      self.gf('django.db.models.fields.CharField')(null=True, blank=True, max_length=4),
                      keep_default=False)
        
        for league in orm['league.League'].objects.all():
            if league.is_tournament_data_filled:
                league = League.objects.get(id=league.id)
                rcl = league.get_total_rating_competitor_list()
                
                for i, lc in enumerate(rcl):
                    if i < 16:
                        lc['lc'].tournament_category = 'A'
                    else:
                        lc['lc'].tournament_category = 'B'
                    
                    lc['lc'].save()

    def backwards(self, orm):
        # Deleting field 'LeagueCompetitor.tournament_category'
        db.delete_column('league_leaguecompetitor', 'tournament_category')


    models = {
        'league.game': {
            'Meta': {'object_name': 'Game'},
            'end_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'league': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['league.League']"}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rating.Location']"}),
            'no_record': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'is_tournament_data_filled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rating.Location']", 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title_ru': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'tournament_a_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'tournament_b_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'league.leaguecompetitor': {
            'Meta': {'object_name': 'LeagueCompetitor'},
            'competitor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rating.Competitor']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_participant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'league': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['league.League']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'tournament_category': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True', 'max_length': '4'}),
            'tournament_place': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
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
            'Meta': {'ordering': "('position',)", 'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'title_ru': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'})
        },
        'rating.competitor': {
            'Meta': {'object_name': 'Competitor'},
            'birthDate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'competitors'", 'symmetrical': 'False', 'to': "orm['rating.Category']"}),
            'firstName': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'firstName_en': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'firstName_ru': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastName': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'lastName_en': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'lastName_ru': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'})
        },
        'rating.location': {
            'Meta': {'object_name': 'Location'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'address_en': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'address_ru': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'title_ru': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['league']
