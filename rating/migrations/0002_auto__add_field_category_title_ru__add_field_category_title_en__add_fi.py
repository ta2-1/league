# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Category.title_ru'
        db.add_column('rating_category', 'title_ru',
                      self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Category.title_en'
        db.add_column('rating_category', 'title_en',
                      self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Rule.text_ru'
        db.add_column('rating_rule', 'text_ru',
                      self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True),
                      keep_default=False)

        # Adding field 'Rule.text_en'
        db.add_column('rating_rule', 'text_en',
                      self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True),
                      keep_default=False)

        # Adding field 'Competitor.firstName_ru'
        db.add_column('rating_competitor', 'firstName_ru',
                      self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Competitor.firstName_en'
        db.add_column('rating_competitor', 'firstName_en',
                      self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Competitor.lastName_ru'
        db.add_column('rating_competitor', 'lastName_ru',
                      self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Competitor.lastName_en'
        db.add_column('rating_competitor', 'lastName_en',
                      self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Location.title_ru'
        db.add_column('rating_location', 'title_ru',
                      self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Location.title_en'
        db.add_column('rating_location', 'title_en',
                      self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Location.address_ru'
        db.add_column('rating_location', 'address_ru',
                      self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Location.address_en'
        db.add_column('rating_location', 'address_en',
                      self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Tournament.title_ru'
        db.add_column('rating_tournament', 'title_ru',
                      self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Tournament.title_en'
        db.add_column('rating_tournament', 'title_en',
                      self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Category.title_ru'
        db.delete_column('rating_category', 'title_ru')

        # Deleting field 'Category.title_en'
        db.delete_column('rating_category', 'title_en')

        # Deleting field 'Rule.text_ru'
        db.delete_column('rating_rule', 'text_ru')

        # Deleting field 'Rule.text_en'
        db.delete_column('rating_rule', 'text_en')

        # Deleting field 'Competitor.firstName_ru'
        db.delete_column('rating_competitor', 'firstName_ru')

        # Deleting field 'Competitor.firstName_en'
        db.delete_column('rating_competitor', 'firstName_en')

        # Deleting field 'Competitor.lastName_ru'
        db.delete_column('rating_competitor', 'lastName_ru')

        # Deleting field 'Competitor.lastName_en'
        db.delete_column('rating_competitor', 'lastName_en')

        # Deleting field 'Location.title_ru'
        db.delete_column('rating_location', 'title_ru')

        # Deleting field 'Location.title_en'
        db.delete_column('rating_location', 'title_en')

        # Deleting field 'Location.address_ru'
        db.delete_column('rating_location', 'address_ru')

        # Deleting field 'Location.address_en'
        db.delete_column('rating_location', 'address_en')

        # Deleting field 'Tournament.title_ru'
        db.delete_column('rating_tournament', 'title_ru')

        # Deleting field 'Tournament.title_en'
        db.delete_column('rating_tournament', 'title_en')


    models = {
        'rating.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'title_ru': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'})
        },
        'rating.competitor': {
            'Meta': {'object_name': 'Competitor'},
            'birthDate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rating.Category']"}),
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
        },
        'rating.results': {
            'Meta': {'object_name': 'Results'},
            'competitor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rating.Competitor']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'place': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'resultset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rating.ResultSet']"})
        },
        'rating.resultset': {
            'Meta': {'object_name': 'ResultSet'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rating.Category']"}),
            'competitors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'resultsets'", 'symmetrical': 'False', 'through': "orm['rating.Results']", 'to': "orm['rating.Competitor']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locations': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'resultsets'", 'symmetrical': 'False', 'to': "orm['rating.Location']"}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rating.Tournament']"})
        },
        'rating.rule': {
            'Meta': {'object_name': 'Rule'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'text_en': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'text_ru': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'})
        },
        'rating.tournament': {
            'Meta': {'object_name': 'Tournament'},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_past': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'squashclub_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'title_ru': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['rating']