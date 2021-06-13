'''
this module is responsible for building limbs

'''


import hou
import control
import constrain
import parameter
import analysis


class build:   

    rig = None
    ctrl = None
    cnst = None
    parmt = None
    ana = None

    COG = None
    root = None
    # = selection.parent()
    

    def __init__(self, rig):


        self.rig = rig

        #self.rig = hou.node('/obj/skel_hum3')

        self.ctrl = control.control(self.rig)

        self.cnst = constrain.constrain(self.rig)

        self.parmt = parameter.parameter(self.rig)

        self.ana = analysis.analysis(self.rig)

        print "builder initialized! "

        self.getRoot()

    def getRoot(self):
        for child in self.rig.children():
            if child.name() == 'root':
                self.root = child

    def getBoneLength(self, bone):
        bone_length = bone.parm('length').eval()
        return bone_length

    def createSpine(self, spine_nodes, spine_nodes_name):

        first_spine = spine_nodes[0]
        second_spine = spine_nodes[1]
        third_spine = spine_nodes[2]
        fourth_spine = spine_nodes[3]
        fifth_spine = spine_nodes[4]
        root = None
        

        for child in self.rig.children():
            if child.name() == 'root':
                root = child


           
        body_part_name = 'Spine'

        # Get rig's PTG
        ptg = self.rig.parmTemplateGroup()

        # create a folder template
        folder = hou.FolderParmTemplate('folder', body_part_name)        



        # Create COG
        COG = self.rig.createNode('null', 'COG_ctrl')
        self.COG = COG
        COG.setParms({'controltype':1, 'orientation': 2})
        #COG.setParms({'tx':})
        COG.setInput(0, second_spine)
        second_spine_length = self.getBoneLength(second_spine)
        COG.setParms({'tz':second_spine_length/2})
        COG.parm('keeppos').set(True)
        COG.setInput(0, None)
        COG.setParms({'rx':0, 'ry':0, 'rz':0})
        COG.moveParmTransformIntoPreTransform()
      

        # Build CVs
        spine_hip_cv = self.rig.createNode('pathcv', 'spine_hip_cv')
        spine_hip_cv.setParms({'sz':0.06})
        spine_hip_cv.setInput(0, first_spine)
        spine_hip_cv.parm('keeppos').set(True)
        spine_hip_cv.setInput(0, None)
        spine_hip_cv.moveParmTransformIntoPreTransform()

        spine_mid_cv = self.rig.createNode('pathcv', 'spine_mid_cv')
        spine_mid_cv.setParms({'sz':0.06})
        spine_mid_cv.setInput(0, fourth_spine)
        spine_mid_cv.parm('keeppos').set(True)
        spine_mid_cv.setInput(0, None)
        spine_mid_cv.moveParmTransformIntoPreTransform()


        spine_chest_cv = self.rig.createNode('pathcv', 'spine_chest_cv')
        spine_chest_cv.setParms({'sz':0.06})
        spine_chest_cv.setInput(0, fifth_spine)
        fifth_spine_length = self.getBoneLength(fifth_spine)
        spine_chest_cv.setParms({'tz':-fifth_spine_length})
        spine_chest_cv.parm('keeppos').set(True)
        spine_chest_cv.setInput(0, None)
        spine_chest_cv.moveParmTransformIntoPreTransform()

        # Build Path
        spine_path = self.rig.createNode('path', 'spine_path')
        for node in spine_path.children():
            if node.name() == 'points_merge':
                node.parm('numobj').set(3)
                node.setParms({
                    'objpath1' : node.relativePathTo(spine_hip_cv) + '/points/',
                    'objpath2' : node.relativePathTo(spine_mid_cv) + '/points/',
                    'objpath3' : node.relativePathTo(spine_chest_cv) + '/points/'
                    })
            if node.name() == "delete_endpoints":
                delete_mid = spine_path.createNode('delete', 'delete_mid_points')
                points_merge = node.inputs()[0]
                connect_points = node.outputs()[0]
                delete_mid.setParms({
                    'group': '4 2',
                    'entity' : 1
                    })
                delete_mid.setInput(0, node)
                connect_points.setInput(0, delete_mid)
            if node.name() == 'output_curve':
                node.setParms({'totype':4})

        # Build IK controls
        hipIk = self.rig.createNode('null', 'Hip_Ik_ctrl')
        midIk = self.rig.createNode('null', 'Mid_Ik_ctrl')
        chestIk = self.rig.createNode('null', 'Chest_Ik_ctrl')

        hipIk.setInput(0, first_spine)
        hipIk.parm('keeppos').set(True)
        hipIk.setInput(0, None)
        hipIk.setParms({'rx':0, 'ry':0, 'rz':0})
        hipIk.setParms({
            'controltype':2,
            'geosizex': 0.5,
            'geosizey': 0.1,
            'geosizez':0.5
            })
        #hipIk.setParms
        hipIk.moveParmTransformIntoPreTransform()

        midIk.setInput(0, fourth_spine)
        midIk.parm('keeppos').set(True)
        midIk.setInput(0, None)
        midIk.setParms({'rx':0, 'ry':0, 'rz':0})
        midIk.setParms({
            'controltype':2,
            'geosizex': 0.5,
            'geosizey': 0.1,
            'geosizez':0.5
            })
        midIk.moveParmTransformIntoPreTransform()

        chestIk.setInput(0, fifth_spine)
        chestIk.parm('keeppos').set(True)
        chestIk.setParms({'tz':-fifth_spine_length})
        chestIk.setInput(0, None)
        chestIk.setParms({'rx':0, 'ry':0, 'rz':0})
        chestIk.setParms({
            'controltype':2,
            'geosizex': 0.5,
            'geosizey': 0.1,
            'geosizez':0.5
            })
        chestIk.moveParmTransformIntoPreTransform()

        spine_hip_cv.setInput(0, hipIk)
        spine_hip_cv.setDisplayFlag(0)

        spine_mid_cv.setInput(0, midIk)
        spine_mid_cv.setDisplayFlag(0)

        spine_chest_cv.setInput(0, chestIk)
        spine_chest_cv.setDisplayFlag(0)

        kin = self.cnst.kinCheck(first_spine)
        spine_kin = kin.createNode('inversekin', 'spinekin')
        spine_kin.setParms({
            'solvertype': 4,
            'bonerootpath':spine_kin.relativePathTo(first_spine),
            'boneendpath':spine_kin.relativePathTo(fifth_spine),
            'curvepath':spine_kin.relativePathTo(spine_path)
            })

        for spine in spine_nodes:
            spine.setParms({'solver': spine.relativePathTo(spine_kin)})

        # Build FK controls
        spine_A_Fk = self.rig.createNode('null', 'spine_A_Fk_ctrl')
        spine_B_Fk = self.rig.createNode('null', 'spine_B_Fk_ctrl')
        spine_C_Fk = self.rig.createNode('null', 'spine_C_Fk_ctrl')

        spine_A_Fk.setInput(0, first_spine)
        spine_A_Fk.parm('keeppos').set(True)
        spine_A_Fk.setInput(0, None)
        spine_A_Fk.setParms({'rx':0, 'ry':0, 'rz':0})
        spine_A_Fk.setParms({
            'controltype':1,
            'geosizex': 1,
            'geosizey': 1,
            'geosizez':1,
            'orientation': 2
            })
        #spine_A_Fk.setParms
        spine_A_Fk.moveParmTransformIntoPreTransform()

        spine_B_Fk.setInput(0, third_spine)
        spine_B_Fk.parm('keeppos').set(True)
        spine_B_Fk.setInput(0, None)
        spine_B_Fk.setParms({'rx':0, 'ry':0, 'rz':0})
        spine_B_Fk.setParms({
            'controltype':1,
            'geosizex': 1,
            'geosizey': 1,
            'geosizez':1,
            'orientation': 2
            })
        spine_B_Fk.moveParmTransformIntoPreTransform()

        spine_C_Fk.setInput(0, fourth_spine)
        spine_C_Fk.parm('keeppos').set(True)
        spine_C_Fk.setParms({'tz':-fifth_spine_length})
        spine_C_Fk.setInput(0, None)
        spine_C_Fk.setParms({'rx':0, 'ry':0, 'rz':0})
        spine_C_Fk.setParms({
            'controltype':1,
            'geosizex': 1,
            'geosizey': 1,
            'geosizez':1,
            'orientation': 2
            })
        spine_C_Fk.moveParmTransformIntoPreTransform()


        # Parent hierarchy
        COG.setInput(0, root)
        spine_A_Fk.setInput(0, COG)
        spine_B_Fk.setInput(0, spine_A_Fk)
        spine_C_Fk.setInput(0, spine_B_Fk)

        hipIk.setInput(0, spine_A_Fk)
        midIk.setInput(0, spine_B_Fk)
        chestIk.setInput(0, spine_C_Fk)

        COG.moveParmTransformIntoPreTransform()
        spine_A_Fk.moveParmTransformIntoPreTransform()
        spine_B_Fk.moveParmTransformIntoPreTransform()
        spine_C_Fk.moveParmTransformIntoPreTransform()
        hipIk.moveParmTransformIntoPreTransform()
        midIk.moveParmTransformIntoPreTransform()
        chestIk.moveParmTransformIntoPreTransform()

        paramNames = self.parmt.makeParameterNames(COG, 'Rot')
        self.parmt.setControllerExpressions(COG, paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(COG, paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(COG, paramNames[0], 'r', 'z')
        cogrparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(cogrparm)
        paramNames = self.parmt.makeParameterNames(COG, 'Trans')
        self.parmt.setControllerExpressions(COG, paramNames[0], 't', 'x')
        self.parmt.setControllerExpressions(COG, paramNames[0], 't', 'y')
        self.parmt.setControllerExpressions(COG, paramNames[0], 't', 'z')
        cogtparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(cogtparm)

        paramNames = self.parmt.makeParameterNames(spine_A_Fk, 'Rot')
        self.parmt.setControllerExpressions(spine_A_Fk, paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(spine_A_Fk, paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(spine_A_Fk, paramNames[0], 'r', 'z')
        spineAparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(spineAparm)

        paramNames = self.parmt.makeParameterNames(spine_B_Fk, 'Rot')
        self.parmt.setControllerExpressions(spine_B_Fk, paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(spine_B_Fk, paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(spine_B_Fk, paramNames[0], 'r', 'z')
        spineBparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(spineBparm)

        paramNames = self.parmt.makeParameterNames(spine_C_Fk, 'Rot')
        self.parmt.setControllerExpressions(spine_C_Fk, paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(spine_C_Fk, paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(spine_C_Fk, paramNames[0], 'r', 'z')
        spineCparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(spineCparm)

        paramNames = self.parmt.makeParameterNames(hipIk, 'Rot')
        self.parmt.setControllerExpressions(hipIk, paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(hipIk, paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(hipIk, paramNames[0], 'r', 'z')
        hipIkrparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(hipIkrparm)
        paramNames = self.parmt.makeParameterNames(hipIk, 'Trans')
        self.parmt.setControllerExpressions(hipIk, paramNames[0], 't', 'x')
        self.parmt.setControllerExpressions(hipIk, paramNames[0], 't', 'y')
        self.parmt.setControllerExpressions(hipIk, paramNames[0], 't', 'z')
        hipIktparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(hipIktparm)

        paramNames = self.parmt.makeParameterNames(midIk, 'Rot')
        self.parmt.setControllerExpressions(midIk, paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(midIk, paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(midIk, paramNames[0], 'r', 'z')
        midIkrparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(midIkrparm)
        paramNames = self.parmt.makeParameterNames(midIk, 'Trans')
        self.parmt.setControllerExpressions(midIk, paramNames[0], 't', 'x')
        self.parmt.setControllerExpressions(midIk, paramNames[0], 't', 'y')
        self.parmt.setControllerExpressions(midIk, paramNames[0], 't', 'z')
        midIktparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(midIktparm)

        paramNames = self.parmt.makeParameterNames(chestIk, 'Rot')
        self.parmt.setControllerExpressions(chestIk, paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(chestIk, paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(chestIk, paramNames[0], 'r', 'z')
        chestIkrparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(chestIkrparm)
        paramNames = self.parmt.makeParameterNames(chestIk, 'Trans')
        self.parmt.setControllerExpressions(chestIk, paramNames[0], 't', 'x')
        self.parmt.setControllerExpressions(chestIk, paramNames[0], 't', 'y')
        self.parmt.setControllerExpressions(chestIk, paramNames[0], 't', 'z')
        chestIktparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(chestIktparm)        



        # append folder to node's parm template group
        ptg.append(folder)

        # set templates to node
        self.rig.setParmTemplateGroup(ptg)

    def createHip(self, hip_nodes, hip_nodes_name):

        hip = hip_nodes[0]

        #hipCtrls = self.CreateFkControlsWithConstraintsSimple( hip, hip.name() )
        hipCtrls = self.ctrl.MakeControlFk(hip, hip.name(), ctrlSize = 0.5)
        self.cnst.MakeFKConstraints(hip, hipCtrls[2])

        hipCtrls[0].setInput(0, self.COG)

    def createArm(self, arm_nodes, body_part_name, twist_local_offset):


        shoulder = arm_nodes[0]
        bicep    = arm_nodes[1]
        forearm  = arm_nodes[2]
        hand     = arm_nodes[3]
        twist    = arm_nodes[4]

        if shoulder.name()[0] == 'L':
            body_part_name = 'L_' + body_part_name
        elif shoulder.name()[0] == 'R':
            body_part_name = 'R_' + body_part_name

        body_part_name += shoulder.name()[-1]        


        # Get rig's PTG
        ptg = self.rig.parmTemplateGroup()

        # create a folder template
        folder = hou.FolderParmTemplate('folder', body_part_name)
        #paramNames = self.parmt.makeParameterNames(body_part_name, 'IkFk')
        parm = hou.FloatParmTemplate(body_part_name + "_ikfk", body_part_name[2:-1] + " IkFk", 1)

        parm.setMaxValue(1)

        # add a parameter template to the folder template
        folder.addParmTemplate(parm)



        #parm = self.parmt.MakeParameter(body_part_name)


        shoulderCtrl = self.ctrl.MakeControlFk(shoulder, shoulder.name(), ctrlSize = 0.5, parm = parm)
        self.cnst.MakeFKConstraints(shoulder, shoulderCtrl[2], parm = parm)
        paramNames = self.parmt.makeParameterNames(shoulder, 'Rot')
        self.parmt.setControllerExpressions(shoulderCtrl[2], paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(shoulderCtrl[2], paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(shoulderCtrl[2], paramNames[0], 'r', 'z')
        sparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(sparm)


        bicepCtrl = self.ctrl.MakeControlFk(bicep, bicep.name(), ctrlSize = 0.5, parm = parm)
        self.cnst.MakeFKConstraints(bicep, bicepCtrl[2], parm = parm)
        paramNames = self.parmt.makeParameterNames(bicep, 'Rot')
        self.parmt.setControllerExpressions(bicepCtrl[2], paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(bicepCtrl[2], paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(bicepCtrl[2], paramNames[0], 'r', 'z')
        bparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(bparm)

        forearmCtrl = self.ctrl.MakeControlFk(forearm, forearm.name(), ctrlSize = 0.5, parm = parm)
        self.cnst.MakeFKConstraints(forearm, forearmCtrl[2], parm = parm)
        paramNames = self.parmt.makeParameterNames(forearm, 'Rot')
        self.parmt.setControllerExpressions(forearmCtrl[2], paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(forearmCtrl[2], paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(forearmCtrl[2], paramNames[0], 'r', 'z')
        fparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(fparm)

        handCtrl = self.ctrl.MakeControlFk(hand, hand.name(), ctrlSize = 0.5, parm = parm)
        self.parmt.setRotExpressions(handCtrl[2], hand)
        paramNames = self.parmt.makeParameterNames(hand, 'Rot')
        self.parmt.setControllerExpressions(handCtrl[2], paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(handCtrl[2], paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(handCtrl[2], paramNames[0], 'r', 'z')
        hparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(hparm)
        
        ik = self.ctrl.MakeIkObjects2(bicep, parm, twist)
        self.cnst.MakeIkConstraints(bicep, ik[0], ik[1], parm)

        goalCtrl = self.ctrl.MakeControlIk(ik[0], ik[0].name(), self.root, ctrlSize = 0.5, parm = parm)

        twistCtrl = self.ctrl.MakeControlIk(ik[1], ik[1].name(), self.root, ctrlSize = 0.5, parm = parm)

        self.cnst.MakeComplexConstraint(hand, handCtrl[2], ik[0], parm)

        paramNames = self.parmt.makeParameterNames(hand, 'goal_Trans')
        self.parmt.setControllerExpressions(goalCtrl[2], paramNames[0], 't', 'x')
        self.parmt.setControllerExpressions(goalCtrl[2], paramNames[0], 't', 'y')
        self.parmt.setControllerExpressions(goalCtrl[2], paramNames[0], 't', 'z')
        gtparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(gtparm)

        paramNames = self.parmt.makeParameterNames(hand, 'goal_Rot')
        self.parmt.setControllerExpressions(goalCtrl[2], paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(goalCtrl[2], paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(goalCtrl[2], paramNames[0], 'r', 'z')
        grparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(grparm)

        paramNames = self.parmt.makeParameterNames(hand, 'twist_Trans')
        self.parmt.setControllerExpressions(twistCtrl[2], paramNames[0], 't', 'x')
        self.parmt.setControllerExpressions(twistCtrl[2], paramNames[0], 't', 'y')
        self.parmt.setControllerExpressions(twistCtrl[2], paramNames[0], 't', 'z')
        tparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(tparm)


        # append folder to node's parm template group
        ptg.append(folder)

        # set templates to node
        self.rig.setParmTemplateGroup(ptg)


        # fingerRoots = self.ana.getChildren(hand)
        # for root in fingerRoots:
        #     chain = [root]
        #     self.ana.walkBones(root, chain, 3)
        #     self.createFinger(chain)

    def createFingers(self, hands):
        fingerRoots = None
        for hand in hands:
            fingerRoots = self.ana.getChildren(hand)
        # ptg = self.rig.parmTemplateGroup()
        # folder = hou.FolderParmTemplate('folder', hand.name())
        for root in fingerRoots:

            #ptg = self.rig.parmTemplateGroup()
            #folder = hou.FolderParmTemplate('folder', root.name())

            chain = [root]
            self.ana.walkBones(root, chain, 3)
            #self.createFinger(chain)
            for finger_bone in chain:
                fk = self.ctrl.MakeControlFk(finger_bone, finger_bone.name(), ctrlSize = 0.1, parm = None)
                self.cnst.MakeFKConstraints(finger_bone, fk[2], parm = None)

                # paramNames = self.parmt.makeParameterNames(finger_bone, 'Rot')
                # self.parmt.setControllerExpressions(fk[2], paramNames[0], 'r', 'x')
                # self.parmt.setControllerExpressions(fk[2], paramNames[0], 'r', 'y')
                # self.parmt.setControllerExpressions(fk[2], paramNames[0], 'r', 'z')
                # fparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
                # folder.addParmTemplate(fparm)
                # ptg.append(folder)
                # self.rig.setParmTemplateGroup(ptg)

    def createFinger(self, finger_nodes):
        for finger_bone in finger_nodes:
            fk = self.ctrl.MakeControlFk(finger_bone, finger_bone.name(), ctrlSize = 0.1, parm = None)
            self.cnst.MakeFKConstraints(finger_bone, fk[2], parm = None)
        
    def createLeg(self, leg_nodes, body_part_name, twist_local_offset):

        thigh = leg_nodes[0]
        shin = leg_nodes[1]
        foot = leg_nodes[2]
        toe = leg_nodes[3]


        if thigh.name()[0] == 'L':
            body_part_name = 'L_' + body_part_name
        elif thigh.name()[0] == 'R':
            body_part_name = 'R_' + body_part_name

        body_part_name += thigh.name()[-1]        

        # Get rig's PTG
        ptg = self.rig.parmTemplateGroup()

        # create a folder template
        folder = hou.FolderParmTemplate('folder', body_part_name)

        parm = hou.FloatParmTemplate(body_part_name + "_ikfk", body_part_name[2:-1] + " IkFk", 1)

        parm.setMaxValue(1)

        # add a parameter template to the folder template
        folder.addParmTemplate(parm)

        # FK

        thighCtrl = self.ctrl.MakeControlFk(thigh, thigh.name(), ctrlSize = 0.5, parm = parm)
        self.cnst.MakeFKConstraints(thigh, thighCtrl[2], parm = parm)
        paramNames = self.parmt.makeParameterNames(thigh, 'Rot')
        self.parmt.setControllerExpressions(thighCtrl[2], paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(thighCtrl[2], paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(thighCtrl[2], paramNames[0], 'r', 'z')
        tparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(tparm)
        
        shinCtrl = self.ctrl.MakeControlFk(shin, shin.name(), ctrlSize = 0.5, parm = parm)
        self.cnst.MakeFKConstraints(shin, shinCtrl[2], parm = parm)
        paramNames = self.parmt.makeParameterNames(shin, 'Rot')
        self.parmt.setControllerExpressions(shinCtrl[2], paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(shinCtrl[2], paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(shinCtrl[2], paramNames[0], 'r', 'z')
        sparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(sparm)
        
        footCtrl = self.ctrl.MakeControlFk(foot, foot.name(), ctrlSize = 0.5, parm = parm)
        self.cnst.MakeFKConstraints(foot, footCtrl[2], parm = parm)
        paramNames = self.parmt.makeParameterNames(foot, 'Rot')
        self.parmt.setControllerExpressions(footCtrl[2], paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(footCtrl[2], paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(footCtrl[2], paramNames[0], 'r', 'z')
        fparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(fparm)
        
        toeCtrl = self.ctrl.MakeControlFk(toe, toe.name(), ctrlSize = 0.5, parm = parm)
        self.cnst.MakeFKConstraints(toe, toeCtrl[2], parm = parm)
        paramNames = self.parmt.makeParameterNames(toe, 'Rot')
        self.parmt.setControllerExpressions(toeCtrl[2], paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(toeCtrl[2], paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(toeCtrl[2], paramNames[0], 'r', 'z')
        toparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(toparm)

        # IK

        ik = self.ctrl.MakeIkObjects(thigh, parm, -twist_local_offset)
        self.cnst.MakeIkConstraints(thigh, ik[0], ik[1], parm)

        ikGoalCtrl = self.ctrl.MakeControlIk(ik[0], ik[0].name(), self.root, ctrlSize = 0.5, parm = parm)
        paramNames = self.parmt.makeParameterNames(thigh, 'Goal_Trans')
        self.parmt.setControllerExpressions(ikGoalCtrl[2], paramNames[0], 't', 'x')
        self.parmt.setControllerExpressions(ikGoalCtrl[2], paramNames[0], 't', 'y')
        self.parmt.setControllerExpressions(ikGoalCtrl[2], paramNames[0], 't', 'z')
        gtparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(gtparm)
        paramNames = self.parmt.makeParameterNames(thigh, 'Goal_Rot')
        self.parmt.setControllerExpressions(ikGoalCtrl[2], paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(ikGoalCtrl[2], paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(ikGoalCtrl[2], paramNames[0], 'r', 'z')
        grparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(grparm)



        ikTwistCtrl = self.ctrl.MakeControlIk(ik[1], ik[1].name(), self.root, ctrlSize = 0.5, parm = parm)
        paramNames = self.parmt.makeParameterNames(thigh, 'Twist_Trans')
        self.parmt.setControllerExpressions(ikTwistCtrl[2], paramNames[0], 't', 'x')
        self.parmt.setControllerExpressions(ikTwistCtrl[2], paramNames[0], 't', 'y')
        self.parmt.setControllerExpressions(ikTwistCtrl[2], paramNames[0], 't', 'z')
        ttparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(ttparm)        

        #self.cnst.MakeComplexConstraint(foot, footCtrl[2], ik[0], parm)

        footIkCtrl = self.ctrl.MakeIkSelfObjects(foot, parm, -twist_local_offset)
        self.cnst.MakeIkSelfConstraint(foot, footIkCtrl[0], footIkCtrl[1], parm)
        
        toeIkCtrl = self.ctrl.MakeIkSelfObjects(toe, parm, -twist_local_offset)
        self.cnst.MakeIkSelfConstraint(toe, toeIkCtrl[0], toeIkCtrl[1], parm)
        
        thighGoal = ik[0]
        thighGoalCtrl = ikGoalCtrl[2]
        footGoal = footIkCtrl[0]
        footTwist = footIkCtrl[1]
        toeGoal = toeIkCtrl[0]
        toeTwist = toeIkCtrl[1]

        thighGoal.setInput(0, None)
        toeGoal.setInput(0, thighGoalCtrl)
        footGoal.setInput(0, toeGoal)
        thighGoal.setInput(0, footGoal)
        toeTwist.setInput(0, footGoal)
        footTwist.setInput(0, thighGoal)

        heelRotCtrl = self.ctrl.MakeCtrl(thighGoal, body_part_name + '_heelRot_ctrl' , ctrlSize = 0.1, parm = parm, flip = True)  
        heelRotCtrl.setInput(0, None)
        heelRotCtrl.setParms({'ty':0, 'tz': -0.2})
        toeGoal.setInput(0, None)
        toeGoal.setInput(0, heelRotCtrl)
        heelRotCtrl.setInput(0, thighGoalCtrl)
        heelRotCtrl.moveParmTransformIntoPreTransform()
        paramNames = self.parmt.makeParameterNames(foot, 'Foot_Rot')
        self.parmt.setControllerExpressions(heelRotCtrl, paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(heelRotCtrl, paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(heelRotCtrl, paramNames[0], 'r', 'z')
        hrparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(hrparm)   

        toeRotCtrl = self.ctrl.MakeCtrl(toeGoal, body_part_name + '_toeRot_ctrl', ctrlSize = 0.1, parm = parm, flip = True)
        toeRotCtrl.setInput(0, None)
        toeGoal.setInput(0, toeRotCtrl)
        toeRotCtrl.setInput(0, heelRotCtrl)
        toeRotCtrl.moveParmTransformIntoPreTransform()
        paramNames = self.parmt.makeParameterNames(toe, 'Toe_Rot')
        self.parmt.setControllerExpressions(toeRotCtrl, paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(toeRotCtrl, paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(toeRotCtrl, paramNames[0], 'r', 'z')
        toerparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(toerparm)

        footRotCtrl = self.ctrl.MakeCtrl(footGoal, body_part_name + '_footRot_ctrl', ctrlSize = 0.1, parm = parm, flip = True)
        footRotCtrl.setInput(0, None)
        footRotCtrl.setInput(0, toeRotCtrl)
        footRotCtrl.moveParmTransformIntoPreTransform()
        footGoal.parm('rx').setExpression("ch('"+footGoal.relativePathTo(footRotCtrl) + "/rx')")
        paramNames = self.parmt.makeParameterNames(foot, 'Ball_Rot')
        self.parmt.setControllerExpressions(footRotCtrl, paramNames[0], 'r', 'x')
        #self.parmt.setControllerExpressions(toeRotCtrl[2], paramNames[0], 'r', 'y')
        #self.parmt.setControllerExpressions(toeRotCtrl[2], paramNames[0], 'r', 'z')
        footrparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(footrparm)
        
        # append folder to node's parm template group
        ptg.append(folder)

        # set templates to node
        self.rig.setParmTemplateGroup(ptg)

    def createQuadLeg(self, leg_nodes, body_part_name, twist_local_offset):
        femur = leg_nodes[0]
        knee = leg_nodes[1]
        ankle = leg_nodes[2]
        foot = leg_nodes[3]
        assist_A = leg_nodes[4]
        assist_B = leg_nodes[5]


        if femur.name()[0] == 'L':
            body_part_name = 'L_' + body_part_name
        elif femur.name()[0] == 'R':
            body_part_name = 'R_' + body_part_name

        body_part_name += femur.name()[-1]        

        # Get rig's PTG
        ptg = self.rig.parmTemplateGroup()

        # create a folder template
        folder = hou.FolderParmTemplate('folder', body_part_name)

        parm = hou.FloatParmTemplate(body_part_name + "_ikfk", body_part_name[2:-1] + " IkFk", 1)

        parm.setMaxValue(1)

        # add a parameter template to the folder template
        folder.addParmTemplate(parm)

        femurCtrl = self.ctrl.MakeControlFk(femur, femur.name(), ctrlSize = 0.5, parm = parm)
        self.cnst.MakeFKConstraints(femur, femurCtrl[2], parm = parm)
        paramNames = self.parmt.makeParameterNames(femur, 'Rot')
        self.parmt.setControllerExpressions(femurCtrl[2], paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(femurCtrl[2], paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(femurCtrl[2], paramNames[0], 'r', 'z')
        fparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(fparm)
        
        kneeCtrl = self.ctrl.MakeControlFk(knee, knee.name(), ctrlSize = 0.5, parm = parm)
        self.cnst.MakeFKConstraints(knee, kneeCtrl[2], parm = parm)
        paramNames = self.parmt.makeParameterNames(knee, 'Rot')
        self.parmt.setControllerExpressions(kneeCtrl[2], paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(kneeCtrl[2], paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(kneeCtrl[2], paramNames[0], 'r', 'z')
        kparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(kparm)
        
        ankleCtrl = self.ctrl.MakeControlFk(ankle, ankle.name(), ctrlSize = 0.5, parm = parm)
        self.cnst.MakeFKConstraints(ankle, ankleCtrl[2], parm = parm)
        paramNames = self.parmt.makeParameterNames(ankle, 'Rot')
        self.parmt.setControllerExpressions(ankleCtrl[2], paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(ankleCtrl[2], paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(ankleCtrl[2], paramNames[0], 'r', 'z')
        aparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(aparm)
        
        footCtrl = self.ctrl.MakeControlFk(foot, foot.name(), ctrlSize = 0.5, parm = parm)
        self.cnst.MakeFKConstraints(foot, footCtrl[2], parm = parm)
        paramNames = self.parmt.makeParameterNames(foot, 'Rot')
        self.parmt.setControllerExpressions(footCtrl[2], paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(footCtrl[2], paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(footCtrl[2], paramNames[0], 'r', 'z')
        ftparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(ftparm)

        # toeCtrl = self.ctrl.MakeControlFk(toe, toe.name(), ctrlSize = 0.5, parm = parm)
        # self.cnst.MakeFKConstraints(toe, toeCtrl[2], parm = parm)
        # paramNames = self.parmt.makeParameterNames(toe, 'Rot')
        # self.parmt.setControllerExpressions(toeCtrl[2], paramNames[0], 'r', 'x')
        # self.parmt.setControllerExpressions(toeCtrl[2], paramNames[0], 'r', 'y')
        # self.parmt.setControllerExpressions(toeCtrl[2], paramNames[0], 'r', 'z')
        # toparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        # folder.addParmTemplate(toparm)


        ik = self.ctrl.MakeIkObjects(femur, parm, -twist_local_offset)
        self.cnst.MakeIkConstraints(femur, ik[0], ik[1], parm)

        ikGoalCtrl = self.ctrl.MakeControlIk(ik[0], ik[0].name(), self.root, ctrlSize = 0.5, parm = parm)
        paramNames = self.parmt.makeParameterNames(femur, 'Goal_Trans')
        self.parmt.setControllerExpressions(ikGoalCtrl[2], paramNames[0], 't', 'x')
        self.parmt.setControllerExpressions(ikGoalCtrl[2], paramNames[0], 't', 'y')
        self.parmt.setControllerExpressions(ikGoalCtrl[2], paramNames[0], 't', 'z')
        gtparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(gtparm)
        # paramNames = self.parmt.makeParameterNames(femur, 'Goal_Rot')
        # self.parmt.setControllerExpressions(ikGoalCtrl[2], paramNames[0], 'r', 'x')
        # self.parmt.setControllerExpressions(ikGoalCtrl[2], paramNames[0], 'r', 'y')
        # self.parmt.setControllerExpressions(ikGoalCtrl[2], paramNames[0], 'r', 'z')
        # grparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        # folder.addParmTemplate(grparm)

        ikTwistCtrl = self.ctrl.MakeControlIk(ik[1], ik[1].name(), self.root, ctrlSize = 0.5, parm = parm)
        paramNames = self.parmt.makeParameterNames(femur, 'Twist_Trans')
        self.parmt.setControllerExpressions(ikTwistCtrl[2], paramNames[0], 't', 'x')
        self.parmt.setControllerExpressions(ikTwistCtrl[2], paramNames[0], 't', 'y')
        self.parmt.setControllerExpressions(ikTwistCtrl[2], paramNames[0], 't', 'z')
        ttparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(ttparm)        

        #self.cnst.MakeComplexConstraint(foot, footCtrl[2], ik[0], parm)

        ankleIkCtrl = self.ctrl.MakeIkSelfObjects(ankle, parm, twist_local_offset)
        self.cnst.MakeIkSelfConstraint(ankle, ankleIkCtrl[0], ankleIkCtrl[1], parm)
        ankleIkCtrl[0].setDisplayFlag(1)
        ankleIkCtrl[0].parm('geoscale').set(0.3)
        paramNames = self.parmt.makeParameterNames(ankle, 'Goal_Trans')
        self.parmt.setControllerExpressions(ankleIkCtrl[0], paramNames[0], 't', 'x')
        self.parmt.setControllerExpressions(ankleIkCtrl[0], paramNames[0], 't', 'y')
        self.parmt.setControllerExpressions(ankleIkCtrl[0], paramNames[0], 't', 'z')
        anktparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(anktparm)
        paramNames = self.parmt.makeParameterNames(ankle, 'Goal_Rot')
        self.parmt.setControllerExpressions(ankleIkCtrl[0], paramNames[0], 'r', 'x')
        self.parmt.setControllerExpressions(ankleIkCtrl[0], paramNames[0], 'r', 'y')
        self.parmt.setControllerExpressions(ankleIkCtrl[0], paramNames[0], 'r', 'z')
        ankrparm = hou.FloatParmTemplate(paramNames[0], paramNames[1], 3)
        folder.addParmTemplate(ankrparm)        

        
        footIkCtrl = self.ctrl.MakeIkSelfObjects(foot, parm, twist_local_offset)
        self.cnst.MakeIkSelfConstraint(foot, footIkCtrl[0], footIkCtrl[1], parm)

        assist_Ik = self.ctrl.MakeIkObjects(assist_A, parm, -twist_local_offset)
        self.cnst.MakeIkConstraints(assist_A, assist_Ik[0], assist_Ik[1], parm)
        #assist_Ik[1].setDisplayFlag(1)
        #assist_Ik[1].parm('geoscale').set(0.3)


        # ankle goal child of root
        root = femur.inputs()[0]
        ankleIkCtrl[0].setInput(0, root)
        ankleIkCtrl[1].setInput(0, root)

        # assist A goal child of ankle goal
        assist_Ik[0].setInput(0, ankleIkCtrl[0])
        assist_Ik[1].setInput(0, root)
        # foot goal child of ankle goal
        footIkCtrl[0].setInput(0, ankleIkCtrl[0])
        footIkCtrl[1].setInput(0, root)
        #femur goal offset child of foot goal
        ikGoalCtrl[0].setInput(0, footIkCtrl[0])


        # append folder to node's parm template group
        ptg.append(folder)

        # set templates to node
        self.rig.setParmTemplateGroup(ptg)

    def createHead(self, head_nodes, body_part_name):

        parm = self.parmt.makeParameter(body_part_name)

        neck = head_nodes[0]
        head = head_nodes[1]


        neckCtrl = self.ctrl.MakeControlFk(neck, neck.name(), ctrlSize = 0.5)
        self.cnst.MakeFKConstraints(neck, neckCtrl[2])

        headCtrl = self.ctrl.MakeControlFk(head, head.name(), ctrlSize = 0.5)
        self.cnst.MakeFKConstraints(head, headCtrl[2])

    def createPiston(self, piston_nodes):

        piston1 = piston_nodes[0]
        piston2 = piston_nodes[1]

        piston1_bone = piston1.outputs()[0]
        piston2_bone = piston2.outputs()[0]

        self.cnst.MakeLookAtContraint(piston1_bone, piston2)
        self.cnst.MakeLookAtContraint(piston2_bone, piston1)

        # base = finger_nodes[0]
        # mid = finger_nodes[1]
        # end = finger_nodes[2]

        # fk_base = self.ctrl.MakeControlFk(base, base.name())
        # self.cnst.MakeFKConstraints(base, fk_base[2])

        # fk_mid = self.ctrl.MakeControlFk(mid, mid.name())
        # self.cnst.MakeFKConstraints(mid, fk_mid[2])

        # fk_end = self.ctrl.MakeControlFk(end, end.name())
        # self.cnst.MakeFKConstraints(end, fk_end[2])

        # print base
        # print mid
        # print end
