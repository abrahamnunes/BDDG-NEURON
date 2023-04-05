#hoc from string 
class optimizedhoc(object):
    def __init__(self,
                 listofparams,
                 condition):
        self.listofparams = listofparams
        self.condition = condition
        self.oh() 

    def oh(self):
        gc = """/**********************       GRANULE CELL         ****************************************

    // extracted from
    // Dentate gyrus network model 
    // Santhakumar V, Aradi I, Soltesz I (2005) J Neurophysiol 93:437-53 
    // https://senselab.med.yale.edu/ModelDB/showModel.cshtml?model=51781&file=\dentategyrusnet2005\DG500_M7.hoc

    // ModelDB file along with publication:
    // Yim MY, Hanuschkin A, Wolfart J (2015) Hippocampus 25:297-308.
    // http://onlinelibrary.wiley.com/doi/10.1002/hipo.22373/abstract

    // modified and augmented by
    // Abraham Nunes / 2022
    // Man Yi Yim / 2015
    // Alexander Hanuschkin / 2011


        TODO: 
            - Pass ndend1/2 as arguments
            - Allow for creation of more than just 2 dendrites

    */

    begintemplate GranuleCell

        ndend1=4
        ndend2=4
        public  pre_list, connect_pre, subsets, is_art, is_connected
        public  vbc2gc, vmc2gc, vhc2gc, vgc2bc, vbc2bc, vmc2bc, vhc2bc, vgc2mc, vbc2mc, vmc2mc, vhc2mc, vgc2hc, vmc2hc
        public soma, gcdend1, gcdend2
        public all, gcldend, pdend, mdend, ddend
        objref all, gcldend, pdend, mdend, ddend

        create soma, gcdend1[ndend1], gcdend2[ndend2]
        objref syn, pre_list

        //to include steady state current injection
        nst=1
        objectvar stim[nst]
        public stim
        // double stimdur[nst], stimdel[nst], stimamp[nst]
        // public stim, stimdur, stimamp, stimdel

        proc init() {
            // Process input arguments 
            // This is ridiculous. There must be a cleaner way. [ TODO ]
            narg = numarg()
            cell_index = $1
            scale_ka_conductances = 1
            scale_km_conductances = 1
            gbar_ht_ = 0 
            gbar_lt_ = 0
            scale_size_ = 1
            scale_gabaa_ = 1
            scale_kir_ = 0
            if (narg > 1) { scale_ka_conductances = $2 }
            if (narg > 2) { scale_km_conductances = $3 }
            if (narg > 3) { gbar_ht_ = $4 }
            if (narg > 4) { gbar_lt_ = $5 }
            if (narg > 5) { scale_size_ = $6 }
            if (narg > 6) { scale_gabaa_ = $7 }
            if (narg > 7) { scale_kir_ = $8 }

            // Run actual initialization 
            pre_list = new List()
            subsets()
            gctemp()
            synapse()
        }

        proc subsets(){ local i
            all = new SectionList()
                soma all.append()
                for i=0, 3 gcdend1 [i] all.append()
                for i=0, 3 gcdend2 [i] all.append()

            gcldend  = new SectionList()
                gcdend1 [0] gcldend.append()
                gcdend2 [0] gcldend.append()

            pdend  = new SectionList()
                gcdend1 [1] pdend.append()
                gcdend2 [1] pdend.append()

            mdend  = new SectionList()
                gcdend1 [2] mdend.append()
                gcdend2 [2] mdend.append()

            ddend  = new SectionList()
                gcdend1 [3] ddend.append()
                gcdend2 [3] ddend.append()
        }
        proc gctemp() {

            scale_area = 1./1.13 * scale_size_

            // ********** Parameters for reversal potentials (assigned below) *********
            e_gabaa_ 	= -70.			// reversal potential GABAA

            // ***************** Parameters
            g_pas_fit_ 	= 1.44e-05 
            gkbar_kir_fit_  = 1.44e-05 * scale_kir_
            ggabaabar_fit_  = 0.722e-05 * scale_gabaa_

            // *********************** PAS ******************************************
            cm_fit_ 	=  1.			
            Ra_fit_ 	=  184. 			// fitted

            // *********************** KIR *****************************************
            vhalfl_kir_fit_ = -98.923594  	// for Botzman I/V curve, fitted
            kl_kir_fit_     = 10.888538 	// for Botzman I/V curve, fitted
            q10_kir_fit_    = 1.			// temperature factor, set to 1
            vhalft_kir_fit_ = 67.0828       // 3 values for tau func from Stegen et al. 2011
            at_kir_fit_     = 0.00610779
            bt_kir_fit_     = 0.0817741

            // ********************* Neuron Morphology etc ***************************
            LJP_ 		= -10.			// Liquid junction potential [mV]
            V_rest 		= -68.16+LJP_   // resting potential [mV]
            V_init 		= -68.16+LJP_   // initial potential [mV]

            // ******************** GABAA ******************** 
            e_pas_fit_	= -83.8
            e_pas_fit_Dend 	= -81.74

            soma {nseg=1 L=16.8*scale_area diam=16.8*scale_area} // changed L & diam
                
            gcdend1 [0] {nseg=1 L=50*scale_area diam=3*scale_area}
            for i = 1, 3	gcdend1 [i] {nseg=1 L=150*scale_area diam=3*scale_area}

            gcdend2 [0] {nseg=1 L=50*scale_area diam=3*scale_area}
            for i = 1, 3	gcdend2 [i] {nseg=1 L=150*scale_area diam=3*scale_area}	

            forsec all {
                insert ccanl
                    catau_ccanl = 10
                    caiinf_ccanl = 5.e-6
                insert HT 
                    gbar_HT = gbar_ht_
                    kan_HT = 0.5
                    kbn_HT = 0.3
                insert LT
                    gbar_LT = gbar_lt_
                Ra=Ra_fit_
            }

            soma {insert bk 						
                    gkbar_bk = %.20f                               // fitted to iPSC [SS]
                insert ichan2  						
                    gnatbar_ichan2 = %.20f                          // fitted to iPSC [SS]
                    el_ichan2 = e_pas_fit_				            // set leak reversal poti to gain Vrest of cell <ah>
                    vshiftma_ichan2 = %.20f                         // fitted to iPSC [SS]
                    vshiftmb_ichan2 = %.20f                         // fitted to iPSC [SS]
                    vshiftha_ichan2 = %.20f                         // fitted to iPSC [SS]
                    vshifthb_ichan2 = %.20f                         // fitted to iPSC [SS]
                    vshiftnfa_ichan2 = %.20f                        // fitted to iPSC [SS]
                    vshiftnfb_ichan2 = %.20f                        // fitted to iPSC [SS]
                    vshiftnsa_ichan2 = %.20f                        // fitted to iPSC [SS]
                    vshiftnsb_ichan2 = %.20f                        // fitted to iPSC [SS]
                    gkfbar_ichan2 = %.20f                           // fitted to iPSC [SS]
                    gksbar_ichan2 = %.20f                           // fitted to iPSC [SS]
                    gl_ichan2 = %.20f                               // fitted to iPSC [SS]
                insert lca 						
                    glcabar_lca = %.20f                             // fitted to iPSC [SS]
                insert nca  						
                    gncabar_nca = %.20f                             // fitted to iPSC [SS]                 
                insert sk						
                    gskbar_sk = %.20f                               // fitted to iPSC [SS]
                insert tca						
                    gcatbar_tca = %.20f                             // fitted to iPSC [SS]
                insert ka 						
                    gkabar_ka = 0.012 * scale_ka_conductances       // Yim et al.
                insert km
                    gbar_km = 0.001 * scale_km_conductances         // Yim et al.
                cm=cm_fit_
            } 

            forsec gcldend { 
                // all values fitted to iPSC except cm [SS]
                insert bk 						
                    gkbar_bk = %.20f                                
                insert ichan2  						
                    gnatbar_ichan2 = %.20f                          
                    el_ichan2 = e_pas_fit_				            // set leak reversal poti to gain Vrest of cell <ah>
                    vshiftma_ichan2 = %.20f                       
                    vshiftmb_ichan2 = %.20f           
                    vshiftha_ichan2 = %.20f            
                    vshifthb_ichan2 = %.20f           
                    vshiftnfa_ichan2 = %.20f                 
                    vshiftnfb_ichan2 = %.20f                      
                    vshiftnsa_ichan2 = %.20f                     
                    vshiftnsb_ichan2 = %.20f             
                    gkfbar_ichan2 = %.20f
                    gksbar_ichan2 = %.20f
                    gl_ichan2 = %.20f
                insert lca 						
                    glcabar_lca = %.20f
                insert nca  						
                    gncabar_nca = %.20f
                insert sk						
                    gskbar_sk = %.20f
                insert tca						
                    gcatbar_tca = %.20f
                cm=cm_fit_
            }
                
            forsec pdend {
                // all values fitted to iPSC except cm [SS]
                insert bk 						
                    gkbar_bk = %.20f
                insert ichan2  						
                    gnatbar_ichan2 = %.20f
                    el_ichan2 = e_pas_fit_				            // set leak reversal poti to gain Vrest of cell <ah>
                    vshiftma_ichan2 = %.20f                       
                    vshiftmb_ichan2 = %.20f           
                    vshiftha_ichan2 = %.20f            
                    vshifthb_ichan2 = %.20f           
                    vshiftnfa_ichan2 = %.20f                 
                    vshiftnfb_ichan2 = %.20f                      
                    vshiftnsa_ichan2 = %.20f                     
                    vshiftnsb_ichan2 = %.20f             
                    gkfbar_ichan2 = %.20f
                    gksbar_ichan2 = %.20f
                    gl_ichan2 = %.20f
                insert lca 						
                    glcabar_lca = %.20f
                insert nca  						
                    gncabar_nca = %.20f
                insert sk						
                    gskbar_sk = %.20f
                insert tca						
                    gcatbar_tca = %.20f
                cm=cm_fit_*1.6
            }
                
            forsec mdend {
                // all values fitted to iPSC except cm [SS]
                insert bk 						
                    gkbar_bk = %.20f
                insert ichan2  						
                    gnatbar_ichan2 = %.20f
                    el_ichan2 = e_pas_fit_				            // set leak reversal poti to gain Vrest of cell <ah>
                    vshiftma_ichan2 = %.20f                       
                    vshiftmb_ichan2 = %.20f           
                    vshiftha_ichan2 = %.20f            
                    vshifthb_ichan2 = %.20f           
                    vshiftnfa_ichan2 = %.20f                 
                    vshiftnfb_ichan2 = %.20f                      
                    vshiftnsa_ichan2 = %.20f                     
                    vshiftnsb_ichan2 = %.20f             
                    gkfbar_ichan2 = %.20f
                    gksbar_ichan2 = %.20f
                    gl_ichan2 = %.20f
                insert lca 						
                    glcabar_lca = %.20f
                insert nca  						
                    gncabar_nca = %.20f
                insert sk						
                    gskbar_sk = %.20f
                insert tca						
                    gcatbar_tca = %.20f
                cm=cm_fit_*1.6
            }

            forsec ddend {
                // all values fitted to iPSC except cm [SS]
                insert bk 						
                    gkbar_bk = %.20f
                insert ichan2  						
                    gnatbar_ichan2 = %.20f
                    el_ichan2 = e_pas_fit_				            // set leak reversal poti to gain Vrest of cell <ah>
                    vshiftma_ichan2 = %.20f                       
                    vshiftmb_ichan2 = %.20f           
                    vshiftha_ichan2 = %.20f            
                    vshifthb_ichan2 = %.20f           
                    vshiftnfa_ichan2 = %.20f                 
                    vshiftnfb_ichan2 = %.20f                      
                    vshiftnsa_ichan2 = %.20f                     
                    vshiftnsb_ichan2 = %.20f             
                    gkfbar_ichan2 = %.20f
                    gksbar_ichan2 = %.20f
                    gl_ichan2 = %.20f
                insert lca 						
                    glcabar_lca = %.20f
                insert nca  						
                    gncabar_nca = %.20f
                insert sk						
                    gskbar_sk = %.20f
                insert tca						
                    gcatbar_tca = %.20f
                cm=cm_fit_*1.6
            }
                
            
            connect gcdend1[0](0), soma(1)
            connect gcdend2[0](0), soma(1)
            for i=1,3 {
                connect gcdend1[i](0), gcdend1[i-1](1)
            }
            for i=1,3 {
                connect gcdend2[i](0), gcdend2[i-1](1)
            }

            forsec all {
                insert kir						// kir conductance added in Yim et al. 2015, note that eK=-90mV is used instead of -105mV as reported in the paper <ah>
                    gkbar_kir       =       gkbar_kir_fit_
                    vhalfl_kir      =       vhalfl_kir_fit_
                    kl_kir          =       kl_kir_fit_
                    vhalft_kir      =       vhalft_kir_fit_
                    at_kir          =       at_kir_fit_
                    bt_kir          =       bt_kir_fit_
                    ggabaa_ichan2 	= 	ggabaabar_fit_		// added GabaA in Yim et al. 2015 <ah> 
                    egabaa_ichan2 	= 	e_gabaa_		// reversal potential GABAA added in Yim et al. 2015 <ah>
                    ena 		    = 	50	        // ena was unified from enat=55 (BC, HIPP, MC) and enat=45 (GC) in Santhakumar et al. (2005) <ah>
                    ek		        =	-90		        // simplified ekf=eks=ek=esk; note the eK was erroneously reported as -105mV in the Yim et al. 2015 <ah>
                    cao_ccanl	    =	2 }
    } // end of gctemp()

        // Retrieval of objref arguments uses the syntax: $o1, $o2, ..., $oi.
        // http://web.mit.edu/neuron_v7.1/doc/help/neuron/general/ocsyntax.html#arguments
        proc connect_pre() {  
            soma $o2 = new NetCon (&v(1), $o1)
        }


        // Define synapses on to GCs using 
        //- an Exp2Syn object (parameters tau1 -rise, tau2 -decay, 
        // time constant [ms] and e - rev potential [mV]
        // delay [ms] and weight -variable betw 0 and 1 [1 corresponding to 1 'S]

        proc synapse() {
            gcdend1[3] syn = new Exp2Syn(0.5) // PP syn based on data from Greg Hollrigel and Kevin Staley   <AH> NOTE: both synapses are identical!
            syn.tau1 = 1.5	syn.tau2 = 5.5	syn.e = 0
            pre_list.append(syn)

            gcdend2[3] syn = new Exp2Syn(0.5) // PP syn based on Greg and Staley
            syn.tau1 = 1.5	syn.tau2 = 5.5	syn.e = 0
            pre_list.append(syn)

            gcdend1[1] syn = new Exp2Syn(0.5) // MC syn *** Estimated
            syn.tau1 = 1.5	syn.tau2 = 5.5	syn.e = 0
            pre_list.append(syn)

            gcdend2[1] syn = new Exp2Syn(0.5) // MC syn   *** Estimated
            syn.tau1 = 1.5	syn.tau2 = 5.5	syn.e = 0
            pre_list.append(syn)

            gcdend1[3] syn = new Exp2Syn(0.5) // HIPP  syn based on Harney and Jones corrected for temp
            syn.tau1 = 0.5	syn.tau2 = 6	syn.e = -70
            pre_list.append(syn)

            gcdend2[3] syn = new Exp2Syn(0.5) // HIPP syn based on Harney and Jones corrected for temp
            syn.tau1 = 0.5	syn.tau2 = 6	syn.e = -70
            pre_list.append(syn)

            soma syn = new Exp2Syn(0.5) // BC  syn  based on Bartos
            syn.tau1 = 0.26	syn.tau2 = 5.5	syn.e = -70
            pre_list.append(syn)

            gcdend1[1] syn = new Exp2Syn(0.5) 								// NOTE: SPROUTED SYNAPSE based on Molnar and Nadler
            syn.tau1 = 1.5	syn.tau2 = 5.5	syn.e = 0
            pre_list.append(syn)

            gcdend2[1] syn = new Exp2Syn(0.5) 								// NOTE: SPROUTED SYNAPSE
            syn.tau1 = 1.5	syn.tau2 = 5.5	syn.e = 0
            pre_list.append(syn)

            // Total of 7 synapses per GC 0,1 PP; 	2,3 MC;	4,5 HIPP and 	6 BC	7,8 Sprout
        }

        func is_art() { return 0 }

    endtemplate GranuleCell
        
        """ %tuple(self.listofparams)

        filename = "GC_%s" %self.condition
        hocfile = open("objects/%s.hoc" %filename, "w")
        hocfile.write(gc)
        hocfile.close() 
