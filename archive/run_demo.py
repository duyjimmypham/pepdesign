from pepdesign.pipeline import PeptideDesignPipeline

def main():
    print("Initializing Peptide Design Pipeline...")
    pipeline = PeptideDesignPipeline()
    
    # Test De Novo Mode
    print("\n\n--- Testing De Novo Mode ---")
    # Using dummy paths since we are using stubs
    results_denovo = pipeline.run_de_novo(
        target_pdb="dummy_target.pdb",
        chain_id="A",
        num_designs=3
    )
    
    print("\nDe Novo Results:")
    for i, res in enumerate(results_denovo):
        print(f"Design {i+1}: ID={res['id']}, Score={res['score']}, Seq={res['sequence']}")

    # Test Optimization Mode
    print("\n\n--- Testing Optimization Mode ---")
    results_opt = pipeline.run_optimization(
        target_pdb="dummy_target.pdb",
        peptide_pdb="dummy_peptide.pdb",
        chain_id="A"
    )
    
    print("\nOptimization Results:")
    for i, res in enumerate(results_opt):
        print(f"Design {i+1}: ID={res['id']}, Score={res['score']}, Seq={res['sequence']}")

if __name__ == "__main__":
    main()
