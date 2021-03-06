import logging
import sys

from src.sgd.convert.transformers import make_db_starter, make_file_starter
from src.sgd.convert import link_gene_names, link_strain_names

__author__ = 'kpaskov'

strain_paragraphs = {'S288C': ('S288C is a widely used laboratory strain, designed by Robert Mortimer for biochemical studies, and specifically selected to be non-flocculent with a minimal set of nutritional requirements.  S288C is the strain used in the systematic sequencing project, the reference sequence stored in SGD. S288C does not form pseudohyphae. In addition, since it has a mutated copy of HAP1, it is not a good strain for mitochondrial studies. It has an allelic variant of MIP1 which increases petite frequency. S288C is gal2- and does not use galactose anaerobically.', [3519363]),
              'RM11-1a': ('RM11-1a is a haploid derivative of RM11, which is a diploid derivative of Bb32(3), which is an ascus derived from Bb32, which is a natural isolate collected by Robert Mortimer from a California vineyard (Ravenswood Zinfandel) in 1993. It has high spore viability (80-90%) and has been extensively characterized phenotypically under a wide range of conditions. It has a significantly longer life span than typical lab yeast strains and accumulates age-associated abnormalities at a lower rate.', [11923494]),
              'YJM789': ('YJM789 is the haploid form of an opportunistic pathogen derived from a yeast isolated from the lung of an immunocompromised patient in 1989. YJM789 has a reciprocal translocation relative to S288C and AWRI1631, between chromosomes VI and X, as well as a large inversion in chromosome XIV. YJM789 is useful for infection studies and quantitative genetics owing to its divergent phenotype, which includes flocculence, heat tolerance, and deadly virulence.', [2671026, 17652520, 18778279]),
              'M22': ('M22 was collected in an Italian vineyard.  It has a reciprocal translocation between chromosomes VIII and XVI relative to S288C. This translocation is common in vineyard and wine yeast strains, leads to increased sulfite resistance.', [18769710, 12368245]),
              'YPS163': ('YPS163 was isolated in 1999 from the soil beneath an oak tree (Quercus rubra) in a Pennsylvania woodland.  YPS163 is freeze tolerant, a phenotype associated with its increased expression of aquaporin AQY2.', [12702333, 15059259]),
              'AWRI1631': ('AWRI1631 is Australian wine yeast, a robust fermenter and haploid derivative of South African commercial wine strain N96.', [18778279]),
              'JAY291': ('JAY291 is a non-flocculent haploid derivative of Brazilian industrial bioethanol strain PE-2; it produces high levels of ethanol and cell mass, and is tolerant to heat and oxidative stress. JAY291 is highly divergent to S288C, RM11-1a and YJM789, and contains well-characterized alleles at several genes of known relation to thermotolerance and fermentation performance.', [19812109]),
              'EC1118': ('EC1118, a diploid commercial yeast, is probably the most widely used wine-making strain worldwide based on volume produced. In the Northern hemisphere, it is also known as Premier Cuvee or Prise de Mousse; it is a reliably aggressive fermenter, and makes clean but somewhat uninteresting wines. EC1118 is more diverged from S288C and YJM789 than from RM11-1a and AWRI1631.  EC1118 has three unique regions from 17 to 65 kb in size on chromosomes VI, XIV and XV, encompassing 34 genes related to key fermentation characteristics, such as metabolism and transport of sugar or nitrogen. There are >100 genes present in S288C that are missing from EC1118.', [19805302]),
              'Sigma1278b': ('Sigma1278b is widely used laboratory strain, and a systematic deletion collection has been constructed in this strain background.  There are 75 genes in Sigma1278b that are absent from S288C. Some non-S288C regions in W303 are also present in Sigma1278b, which exhibits six times the rate of sequence divergence to S288C as seen in W303.  Sigma1278b is identical to S288C at less than half its genome.', [20413493]),
              'FostersO': ("Foster's O is a commercial ale strain which has a whole-chromosome amplification of chromosome III.  Foster's O has 48 ORFs not present in S288C.", [21304888]),
              'FostersB': ("Foster's B is a commercial ale strain which has whole-chromosome amplifications of chromosomes II, V and XV. Foster's B has 36 ORFs not present in S288C.", [21304888]),
              'VIN13': ('VIN13 is a cold-tolerant South African wine strain, a strong fermenter that is good for making aromatic white wines.  VIN13 has 45 ORFs not present in S288C.', [21304888]),
              'AWRI796': ("AWRI796 is a South African wine strain that ferments more successfully at warmer temperatures and is more suited to the production of reds. AWRI796 has a whole-chromosome amplification of chromosome I.  AWRI has 74 ORFs that are not present in S288C.", [21304888]),
              'CLIB215': ("CLIB215 was isolated in 1994 from a bakery in Taranaki in the North Island of New Zealand.", []),
              'CBS7960': ("CBS7960 was isolated from a cane sugar bioethanol factory in Sao Paulo, Brazil.", []),
              'CLIB324': ("CLIB324 is a Vietnamese baker's strain collected in 1996 from Ho Chi Minh City.", []),
              'CLIB382': ("CLIB382 was isolated from beer brewed in Ireland sometime before 1952.", []),
              'EC9-8': ("EC9-8 is a haploid cadmium-resistant derivative of a yeast isolated from the valley bottom of Evolution Canyon at Lower Nahal Oren, Israel.", [21483812]),
              'FL100': ("FL100 is a commonly used laboratory strain.  FL100 has a duplication of 80 kb of chromosome III on the left arm chromosome I, and has lost ~45 kb from right end of chromosome I.", [9605505]),
              'Kyokai7': ("Kyokai No. 7 (K7) is the most extensively used sake yeast, and was first isolated from a sake brewery in Nagano Prefecture, Japan, in 1946.  K7 has two large inversions on chromosomes V and XIV, both flanked by transposable elements and inverted repeats, two CNV reductions on chromosomes I and VII and a mosaic-like pattern and non-random distribution of variation compared with S288C. There are 48 ORFs in K7 that are absent in S288C, and 49 ORFs in S288C that are missing from K7.", [21900213]),
              'LalvinQA23': ("QA23 is a cold-tolerant Portuguese wine strain from the Vinho Verde region. QA23 has low nutrient and oxygen requirements, and exhibits high beta-glucosidase activity, a combination that makes beautiful Sauvignon blancs. QA23 has 110 ORFs that are not present in S288C.", [21304888]),
              'PW5': ("PW5 was isolated from fermented sap of a Raphia palm tree in Aba, Abia state, Nigeria in 2002. PW5 shares with YJM269 and CEN.PK113-7D some genes that are absent from S288C.", [22448915]),
              'T7': ("T7 was isolated from oak tree exudate in Missouri's Babler State Park. ", []),
              'T73': ("T73 is from a Mourvedre (aka Monastrell) red wine made in Alicante, Spain, in 1987. T73 has low nitrogen requirements, high alcohol tolerance and low volatile acidity production, making it ideal for fermenting robust structured reds grown in hot climates.", []),
              'UC5': ("UC5 came from Sene sake in Kurashi, Japan, sometime before 1974.", []),
              'VL3': ("VL3 was isolated in Bordeaux, France, and is most suited to the production of premium aromatic white wines with high thiol content (citrus and tropical fruit characters). VL3 has a whole-chromosome amplification of chromosome VIII, as well as 54 ORFs that are missing from S288C.", [21304888]),
              'W303': ("W303-derivative K6001 is a key model organism for research into aging, and shares >85% of its genome with S288C, differing at >8000 nucleotide positions, causing changes to the sequences of 799 proteins. These differences are distributed non-randomly throughout the genome, with chromosome XVI being almost identical between the two strains, and chromosome XI the most divergent. Some of the non-S288C regions in W303 are also present in Sigma1278b.", [22977733]),
              'Y10': ("Y10 was isolated from a coconut in the Philippines, sometime before 1973.", []),
              'YJM269': ("YJM269 came from red Blauer Portugieser grapes in Austria in 1954. YJM269 shares with CEN.PK113-7D some genes that are absent from S288C, including the ENA6 sodium pump, and others that are also found in PW5.", [22448915]),
              'BY4741': ("BY4741 is part of a set of deletion strains derived from S288C in which commonly used selectable marker genes were deleted by design in order to minimize or eliminate homology to the corresponding marker genes in commonly used vectors without significantly affecting adjacent gene expression. The yeast strains were all directly descended from FY2, which is itself a direct descendant of S288C. Variation between BY4741 and S288C is miniscule. BY4741 was used as a parent strain for the international systematic <i>Saccharomyces cerevisiae</i> gene disruption project.", [9483801, 7762301]),
              'BY4742': ("BY4742 is part of a set of deletion strains derived from S288C in which commonly used selectable marker genes were deleted by design in order to minimize or eliminate homology to the corresponding marker genes in commonly used vectors without significantly affecting adjacent gene expression. The yeast strains were all directly descended from FY2, which is itself a direct descendant of S288C. Variation between BY4742 and S288C is miniscule. BY4742 was used as a parent strain for the international systematic <i>Saccharomyces cerevisiae</i> gene disruption project.", [9483801, 7762301]),
              'CENPK': ("CEN.PK113-7D is a laboratory strain derived from parental strains ENY.WA-1A and MC996A, and is popular for use in systems biology studies. There are six duplicated regions in CEN.PK113-7D relative to S288C, two on chromosome II, and one each on chromosomes III, VII, VIII and XV, including an enrichment of maltose metabolism genes. CEN.PK113-7D is a biotin prototroph, and has genes required for biotin biosynthesis. There are >20,000 SNPs between CEN.PK113-7D and S288C, two-thirds of which are within ORFs. Almost 5000 of these result in altered sequences of >1400 proteins. There are also >2800 small indels averaging 3 bp each in CEN.PK113-7D relative to S288C, and more than 400 of these are in coding regions. CEN.PK113-7D also has an additional 83 genes that are absent from S288C, including the ENA6 sodium pump that is also found in YJM269, and others that are present in both YJM269 and PW5.", [22448915]),
              'ZTW1': ("ZTW1 was isolated from corn mash used for industrial bioethanol production in China in 2007.", []),
              'AB972': ('AB972 is an ethidium bromide-induced [rho<sup>0</sup>] derivative of Robert Mortimer\'s X2180-1B (obtained via Elizabeth Jones), itself a haploid derivative of strain X2180, which was made by self-diploidization of S288C. AB972 was used in the original sequencing project for chromosomes I, III, IV, V, VI, VIII, IX, XII, XIII, and XVI.  A single colony of AB972 was also later used as the source of DNA for the latest <i>S. cerevisiae</i> version R64 genomic reference sequence (also known as S288C 2010). This single colony was grown from a stored isolate from the original AB972 strain used by Linda Riles to create the DNA libraries used in the original genome project.', [2029969, 3463999, 3519363, 8514151, 7731988, 1574125, 9169867, 9169868, 7670463, 8091229, 9169870, 9169871, 9169872, 9169875, 24374639]),
              'FY1679': ('FY1679 is a diploid made from haploid parents FY23 (mating type a) and FY73 (mating type &alpha;) by Fred Winston and colleagues who used gene replacement to develop a set of yeast strains isogenic to S288C but repaired for GAL2, and which also contained nonreverting mutations in several genes commonly used for selection in the laboratory environment (URA3, TRP1, LYS2, LEU2, HIS3). A cosmid library made from FY1679 was used in the original genome sequencing project as the source of DNA for chromosomes VII, X, XI, XIV, and XV. FY1679 was also used for sequencing the mitochondrial DNA, which was not part of the nuclear genome project and was determined separately.', [7762301, 9169869, 8641269, 8196765, 9169873, 9169874, 9872396, 1964349]),
              'FY4': ('FY4 was made by Fred Winston and colleagues who used gene replacement to develop a set of yeast strains isogenic to S288C but repaired for GAL2, and which also contained nonreverting mutations in several genes commonly used for selection in the laboratory environment (URA3, TRP1, LYS2, LEU2, HIS3).', [7762301])

}

# --------------------- Convert Bioentity Paragraph ---------------------
def create_i(reference, reference_index):
    new_i = '<span data-tooltip aria-haspopup="true" class="has-tip" title="' + reference.display_name + '"><a href="#reference">' + str(reference_index) + '</a></span>'
    return new_i

def clean_paragraph(locus, text, label, sgdid_to_reference, sgdid_to_bioentity, goid_to_go):
    reference_id_to_index = {}
    for reference in locus.get_ordered_references():
        reference_id_to_index[reference.id] = len(reference_id_to_index) + 1

    # Replace bioentities
    feature_blocks = text.split('<feature:')
    if len(feature_blocks) > 1:
        new_bioentity_text = feature_blocks[0]
        for block in feature_blocks[1:]:
            end_index = block.find('>')
            final_end_index = block.find('</feature>')
            if final_end_index > end_index >= 0:
                try:
                    if block[1:end_index].endswith('*'):
                        replacement = '<a href="/cgi-bin/search/luceneQS.fpl?query=' + block[1:end_index] + '">' + block[end_index+1:final_end_index] + '</a>'
                        new_bioentity_text += replacement
                    else:
                        sgdid = 'S' + block[1:end_index].zfill(9)
                        if sgdid in sgdid_to_bioentity:
                            bioentity = sgdid_to_bioentity[sgdid]
                            replacement = '<a href="' + bioentity.link + '">' + block[end_index+1:final_end_index] + '</a>'
                            new_bioentity_text += replacement
                        else:
                            print 'Feature not found in ' + label + ' : ' + block[0:end_index]
                except:
                    print 'Bad sgdid in ' + label + ' : ' + block[0:end_index]

                new_bioentity_text += block[final_end_index+10:]
            else:
                new_bioentity_text += block
    else:
        new_bioentity_text = text

    # Replace go
    go_blocks = new_bioentity_text.split('<go:')
    if len(go_blocks) > 1:
        new_go_text = go_blocks[0]
        for block in go_blocks[1:]:
            end_index = block.find('>')
            final_end_index = block.find('</go>')
            if final_end_index > end_index >= 0:
                try:
                    goid = int(block[0:end_index])
                    if goid in goid_to_go:
                        go = goid_to_go[goid]
                        replacement = '<a href="' + go.link + '">' + block[end_index+1:final_end_index] + '</a>'
                        new_go_text += replacement
                    else:
                        print 'Go not found in ' + label + ' : ' + block[0:end_index]
                except:
                    print 'Bad goid in ' + label + ' : ' + block[0:end_index]

                new_go_text += block[final_end_index+5:]
            else:
                new_go_text += block
    else:
        new_go_text = new_bioentity_text

    # Replace MetaCyc
    metacyc_blocks = new_go_text.split('<MetaCyc:')
    if len(metacyc_blocks) > 1:
        new_metacyc_text = metacyc_blocks[0]
        for block in metacyc_blocks[1:]:
            end_index = block.find('>')
            final_end_index = block.find('</MetaCyc>')
            if final_end_index > end_index >= 0:
                replacement = '<a href="http://pathway.yeastgenome.org/YEAST/NEW-IMAGE?type=PATHWAY&object=' + block[0:end_index] + '">' + block[end_index+1:final_end_index] + '</a>'
                new_metacyc_text += replacement
                new_metacyc_text += block[final_end_index+10:]
            else:
                new_metacyc_text += block
    else:
        new_metacyc_text = new_go_text

    # Replace OMIM
    omim_blocks = new_metacyc_text.split('<OMIM:')
    if len(omim_blocks) > 1:
        new_omim_text = omim_blocks[0]
        for block in omim_blocks[1:]:
            end_index = block.find('>')
            final_end_index = block.find('</OMIM>')
            if final_end_index > end_index >= 0:
                replacement = '<a href="http://www.omim.org/entry/' + block[0:end_index] + '">' + block[end_index+1:final_end_index] + '</a>'
                new_omim_text += replacement
                new_omim_text += block[final_end_index+7:]
            else:
                new_omim_text += block
    else:
        new_omim_text = new_metacyc_text

    # Replace references
    reference_blocks = new_omim_text.split('<reference:')
    if len(reference_blocks) > 1:
        new_reference_text = reference_blocks[0]
        for block in reference_blocks[1:]:
            end_index = block.find('>')
            if end_index >= 0:
                sgdid = block[0:end_index]
                reference = None if sgdid not in sgdid_to_reference else sgdid_to_reference[sgdid]
                if reference is not None:
                    reference_index = '?' if reference.id not in reference_id_to_index else reference_id_to_index[reference.id]
                    replacement = create_i(reference, reference_index)
                else:
                    raise Exception("Could not find reference sgdid: " + sgdid)

                new_reference_text += replacement
                new_reference_text += block[end_index+1:]
            else:
                new_reference_text += block
    else:
        new_reference_text = new_omim_text

    return new_reference_text, text

def make_bioentity_paragraph_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.nex.bioconcept import Go
    from src.sgd.model.bud.general import ParagraphFeat
    from src.sgd.model.bud.go import GoFeature
    from src.sgd.model.bud.feature import Feature
    from datetime import datetime

    def bioentity_paragraph_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in nex_session.query(Locus).all()])
        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Locus).all()])
        sgdid_to_reference = dict([(x.sgdid, x) for x in nex_session.query(Reference).all()])
        sgdid_to_bioentity = dict([(x.sgdid, x) for x in nex_session.query(Bioentity).all()])
        goid_to_go = dict([(int(x.go_id[3:]), x) for x in nex_session.query(Go).all()])

        #LSP
        for feature in bud_session.query(Feature).all():
            paragraph_feats = feature.paragraph_feats
            if len(paragraph_feats) > 0 and feature.id in id_to_bioentity:
                paragraph_feats.sort(key=lambda x: x.order)
                paragraph_html, paragraph_text = clean_paragraph(id_to_bioentity[feature.id], '<p>' + ('</p><p>'.join([x.paragraph.text for x in paragraph_feats])) + '</p>', str([x.paragraph.id for x in paragraph_feats]), sgdid_to_reference, sgdid_to_bioentity, goid_to_go)
                
                date_edited = None
                year = 0
                month = 0
                day = 0
                for paragraph_feat in paragraph_feats:
                    my_date = paragraph_feat.paragraph.date_edited
                    this_date = str(my_date).split(' ')[0].replace('-0', '-').split('-')
                    this_year = int(this_date[0])
                    this_month = int(this_date[1])
                    this_day = int(this_date[2])
                    if date_edited is None or datetime(this_year, this_month, this_day) > datetime(year, month, day):
                        date_edited = my_date
                        year = this_year
                        month = this_month
                        day = this_day

                yield {
                    'bioentity': id_to_bioentity[feature.id],
                    'source': key_to_source['SGD'],
                    'text': paragraph_text,
                    'html': paragraph_html,
                    'date_edited': date_edited,
                    'date_created': paragraph_feats[0].paragraph.date_created,
                    'created_by': paragraph_feats[0].paragraph.created_by,
                    'category': 'LSP'
                }

        bioentity_key_to_date = dict()
        #Go
        for gofeature in bud_session.query(GoFeature).all():
            bioentity_key = (gofeature.feature.name, 'LOCUS')
            if gofeature.annotation_type == 'manually curated' and bioentity_key not in bioentity_key_to_date:
                bioentity_key_to_date[bioentity_key] = gofeature.date_last_reviewed

        for bioentity_key, date_last_reviewed in bioentity_key_to_date.iteritems():
            if bioentity_key in key_to_bioentity:
                yield {
                    'bioentity': key_to_bioentity[bioentity_key],
                    'source': key_to_source['SGD'],
                    'text': str(date_last_reviewed),
                    'html': str(date_last_reviewed),
                    'date_created': None,
                    'created_by': None,
                    'category': 'GODATE'
                }
            else:
                #print 'Bioentity not found: ' + str(bioentity_key)
                yield None

        for pieces in make_file_starter('src/sgd/convert/data/gp_information.559292_sgd')():
            if len(pieces) >= 8:
                sgdid = pieces[8]
                if sgdid.startswith('SGD:'):
                    sgdid = sgdid[4:]
                    go_annotation = [x[22:].strip() for x in pieces[9].split('|') if x.startswith('go_annotation_summary')]
                    if len(go_annotation) == 1:
                        if sgdid in sgdid_to_bioentity:
                            yield {
                                'bioentity': sgdid_to_bioentity[sgdid],
                                'source': key_to_source['SGD'],
                                'text': go_annotation[0],
                                'html': go_annotation[0],
                                'date_created': None,
                                'created_by': None,
                                'category': 'GO'
                            }
                        else:
                            print 'Bioentity not found: ' + sgdid
                            yield None

        #Regulation
        file_names = ['src/sgd/convert/data/regulationSummaries',
                      'src/sgd/convert/data/15-8regulationSummaries.txt',
                      'src/sgd/convert/data/15-9regulationSummaries.txt',
                      'src/sgd/convert/data/15-10regulationSummaries.txt',
                      'src/sgd/convert/data/15-11regulationSummaries.txt',
                      'src/sgd/convert/data/16-1regulationSummaries.txt',
                      'src/sgd/convert/data/16-2regulationSummaries.txt',
                      'src/sgd/convert/data/16-3regulationSummaries.txt',
                      'src/sgd/convert/data/16-4regulationSummaries.txt',
                      'src/sgd/convert/data/16-5regulationSummaries.txt']

        for file_name in file_names:
            for row in make_file_starter(file_name)():
                bioentity_key = (row[0], 'LOCUS')

                if bioentity_key in key_to_bioentity:
                    bioentity = key_to_bioentity[bioentity_key]
                    yield {
                        'bioentity': bioentity,
                        'source': key_to_source['SGD'],
                        'text': row[2],
                        'html': link_gene_names(row[2], {bioentity.display_name, bioentity.format_name, bioentity.display_name + 'P', bioentity.format_name + 'P'}, nex_session),
                        'category': 'REGULATION'
                    }
                else:
                    #print 'Bioentity not found: ' + str(bioentity_key)
                    yield None

        #Phenotype
        file_names = ['src/sgd/convert/data/PhenotypeSummaries032015.txt',
                      'src/sgd/convert/data/15-6phenoSummariesTyposFixed.txt',
                      'src/sgd/convert/data/15-7phenoSummaries.txt',
                      'src/sgd/convert/data/15-8phenoSummaries.txt',
                      'src/sgd/convert/data/15-9phenoSummaries.txt',
                      'src/sgd/convert/data/15-10phenoSummaries.txt',
                      'src/sgd/convert/data/15-11phenoSummaries.txt',
                      'src/sgd/convert/data/15-12phenoSummaries.txt',
                      'src/sgd/convert/data/16-1phenoSummaries.txt',
                      'src/sgd/convert/data/16-2phenoSummaries.txt',
                      'src/sgd/convert/data/16-3phenoSummaries.txt',
                      'src/sgd/convert/data/16-4phenoSummaries.txt',
                      'src/sgd/convert/data/16-5phenoSummaries.txt',
                      'src/sgd/convert/data/16-6phenoSummaries.txt',
                      'src/sgd/convert/data/16-7phenoSummaries.txt',
                      'src/sgd/convert/data/16-9phenoSummaries.txt',
                      'src/sgd/convert/data/16-10phenoSummaries.txt']

        for file_name in file_names:
            for row in make_file_starter(file_name)():
                bioentity_key = (row[0], 'LOCUS')
                if bioentity_key in key_to_bioentity:
                    bioentity = key_to_bioentity[bioentity_key]
                    yield {
                        'bioentity': bioentity,
                        'source': key_to_source['SGD'],
                        'text': row[1],
                        'html': link_gene_names(row[1], {bioentity.display_name, bioentity.format_name, bioentity.display_name + 'P', bioentity.format_name + 'P'}, nex_session),
                        'category': 'PHENOTYPE'
                        }
                else:
                    #print 'Bioentity not found: ' + str(bioentity_key)
                    yield None


        bud_session.close()
        nex_session.close()
    return bioentity_paragraph_starter

# --------------------- Convert Strain Paragraph ---------------------
def make_strain_paragraph_starter(nex_session_maker):
    from src.sgd.model.nex.misc import Source, Strain
    def strain_paragraph_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in nex_session.query(Strain).all()])

        #Strain
        for strain_key, paragraph in strain_paragraphs.iteritems():
            if strain_key in key_to_strain:
                text = paragraph[0]
                html = link_gene_names(text, {'HO'}, nex_session)
                html = link_strain_names(html, {key_to_strain[strain_key].display_name}, nex_session)
                yield {
                    'source': key_to_source['SGD'],
                    'text': text,
                    'html': html,
                    'strain': key_to_strain[strain_key],
                }
            else:
                print 'Strain not found: ' + str(strain_key)
                yield None

        nex_session.close()
    return strain_paragraph_starter

# --------------------- Convert Reference Paragraph ---------------------
def make_reference_paragraph_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.reference import Abstract
    from src.sgd.model.nex.reference import Reference
    def reference_paragraph_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])

        for old_abstract in make_db_starter(bud_session.query(Abstract), 1000)():
            reference_id = old_abstract.reference_id
            if reference_id in id_to_reference:
                yield {
                    'source': key_to_source['SGD'],
                    'text': old_abstract.text,
                    'html': link_gene_names(old_abstract.text, set(), nex_session),
                    'reference': id_to_reference[reference_id],
                }
            else:
                print 'Reference not found: ' + str(reference_id)
                yield None

        bud_session.close()
        nex_session.close()
    return reference_paragraph_starter

# --------------------- Convert ParagraphReference ---------------------
def make_paragraph_reference_starter(nex_session_maker):
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.paragraph import Paragraph
    from src.sgd.model.nex.reference import Reference
    def paragraph_reference_starter():
        nex_session = nex_session_maker()

        references = nex_session.query(Reference).all()
        key_to_paragraph = dict([(x.unique_key(), x) for x in nex_session.query(Paragraph).all()])
        pubmed_id_to_reference = dict([(x.pubmed_id, x) for x in references])
        sgdid_to_reference = dict([(x.sgdid, x) for x in references])

        #LSP
        for paragraph in key_to_paragraph.values():
            if paragraph.category == 'LSP':
                sgdids = [x.split('>')[0] for x in paragraph.text.split('<reference:')]
                for sgdid in sgdids:
                    if sgdid in sgdid_to_reference:
                        reference = sgdid_to_reference[sgdid]
                        yield {
                                'paragraph_id': paragraph.id,
                                'reference_id': reference.id
                            }
                    else:
                        if sgdid != '<p':
                            print 'Reference not found: ' + sgdid

        #Regulation
        file_names = ['src/sgd/convert/data/regulationSummaries',
                      'src/sgd/convert/data/15-8regulationSummaries.txt',
                      'src/sgd/convert/data/15-9regulationSummaries.txt',
                      'src/sgd/convert/data/15-10regulationSummaries.txt',
                      'src/sgd/convert/data/15-11regulationSummaries.txt',
                      'src/sgd/convert/data/16-1regulationSummaries.txt',
                      'src/sgd/convert/data/16-2regulationSummaries.txt',
                      'src/sgd/convert/data/16-3regulationSummaries.txt',
                      'src/sgd/convert/data/16-4regulationSummaries.txt',
                      'src/sgd/convert/data/16-5regulationSummaries.txt']

        for file_name in file_names:
            for row in make_file_starter(file_name)():
                paragraph_key = (row[0], 'BIOENTITY', 'REGULATION')
                for pubmed_id in [int(x) for x in row[3].strip().split('|') if x != 'references' and x != '']:
                    if paragraph_key in key_to_paragraph and pubmed_id in pubmed_id_to_reference:
                        yield {
                            'paragraph_id': key_to_paragraph[paragraph_key].id,
                            'reference_id': pubmed_id_to_reference[pubmed_id].id,
                        }
                    else:
                        print 'Paragraph or reference not found: ' + str(paragraph_key) + ' ' + str(pubmed_id)
                        yield None

        #Strain
        for strain_key, paragraph in strain_paragraphs.iteritems():
            paragraph_key = (strain_key, 'STRAIN', None)
            for pubmed_id in paragraph[1]:
                if paragraph_key in key_to_paragraph and pubmed_id in pubmed_id_to_reference:
                    yield {
                        'paragraph_id': key_to_paragraph[paragraph_key].id,
                        'reference_id': pubmed_id_to_reference[pubmed_id].id,
                    }
                else:
                    print 'Paragraph or reference not found: ' + str(paragraph_key) + ' ' + str(pubmed_id)
                    yield None



        nex_session.close()
    return paragraph_reference_starter
