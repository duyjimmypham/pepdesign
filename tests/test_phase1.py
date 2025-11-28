"""
Test script for Phase 1 architecture.
Verifies TargetState, RosettaRelaxer, and prepare_target refactor.
"""
import os
import shutil
from pepdesign.modules.prepare_target import prepare_target
from pepdesign.models import TargetState, PeptideInfo
from pepdesign.external.rosetta import get_relaxer, MockRelaxer

def test_phase1_architecture():
    print("Testing Phase 1 Architecture...")
    
    # Setup
    test_pdb = "tests/dummy_test.pdb"
    if not os.path.exists(test_pdb):
        print("Creating dummy PDB...")
        # create a minimal PDB file
        with open(test_pdb, "w") as f:
            f.write("ATOM      1  N   ALA A   1      10.000  10.000  10.000  1.00  0.00           N\n")
            f.write("ATOM      2  CA  ALA A   1      11.458  10.000  10.000  1.00  0.00           C\n")
            f.write("ATOM      3  C   ALA A   1      12.000  11.400  10.000  1.00  0.00           C\n")
            f.write("ATOM      4  O   ALA A   1      11.500  12.300  10.000  1.00  0.00           O\n")
            f.write("ATOM      5  CB  ALA A   1      12.000   9.000  10.000  1.00  0.00           C\n")
    
    output_dir = "test_phase1_output"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        
    # Test 1: OpenMMRelaxer Factory
    print("\n[Test 1] OpenMMRelaxer Factory")
    from pepdesign.external.openmm import get_openmm_relaxer, MockOpenMMRelaxer
    relaxer = get_openmm_relaxer()
    # It might be Mock or Real depending on environment.
    # We just want to ensure it returns a valid relaxer.
    assert hasattr(relaxer, 'relax')
    print(f"  ✓ Relaxer obtained: {type(relaxer).__name__}")
    
    # Test 2: prepare_target (De Novo)
    print("\n[Test 2] prepare_target (De Novo)")
    state = prepare_target(
        pdb_path=test_pdb,
        output_dir=output_dir,
        mode="de_novo",
        target_chain="A",
        do_relax=True
    )
    
    assert isinstance(state, TargetState)
    assert os.path.exists(state.pdb_path)
    assert state.relaxed_pdb_path is not None
    assert os.path.exists(state.relaxed_pdb_path)
    assert state.binding_site.source == "auto_stub"
    print("  ✓ TargetState created successfully")
    print(f"  ✓ Clean PDB: {state.pdb_path}")
    print(f"  ✓ Relaxed PDB: {state.relaxed_pdb_path}")
    
    # Test 3: prepare_target (Optimize Existing - Mock)
    # We need a PDB with two chains for this.
    print("\n[Test 3] prepare_target (Optimize Existing)")
    test_complex_pdb = "tests/dummy_complex.pdb"
    with open(test_complex_pdb, "w") as f:
        # Chain A (Target)
        f.write("ATOM      1  N   ALA A   1      10.000  10.000  10.000  1.00  0.00           N\n")
        f.write("ATOM      2  CA  ALA A   1      11.458  10.000  10.000  1.00  0.00           C\n")
        # Chain B (Peptide) - close to Chain A
        f.write("ATOM     10  N   ALA B   1      15.000  10.000  10.000  1.00  0.00           N\n")
        f.write("ATOM     11  CA  ALA B   1      16.458  10.000  10.000  1.00  0.00           C\n")
        
    state_opt = prepare_target(
        pdb_path=test_complex_pdb,
        output_dir=output_dir + "_opt",
        mode="optimize_existing",
        target_chain="A",
        peptide_chain="B",
        do_relax=False
    )
    
    assert state_opt.peptide_info is not None
    assert state_opt.peptide_info.chain_id == "B"
    assert state_opt.peptide_info.sequence == "A" # ALA -> A
    assert state_opt.binding_site.source == "from_peptide"
    print("  ✓ PeptideInfo extracted successfully")
    print(f"  ✓ Peptide Sequence: {state_opt.peptide_info.sequence}")

    print("\n✅ Phase 1 Verification Passed!")

if __name__ == "__main__":
    test_phase1_architecture()
