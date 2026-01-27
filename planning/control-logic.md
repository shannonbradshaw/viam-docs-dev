 ---
  **STATUS: IMPLEMENTED** - See try/stationary-vision/part3.md and part4.md

  Detailed Summary: Updated Parts 3 and 4 Using viam module generate                            
                                                                                                
  Key Insight: Preserving Iteration                                                             
                                                                                                
  The generator gives us a CLI for testing, so we can still iterate:                            
  1. Generate scaffold → test connection                                                        
  2. Add detection logic → test detection                                                       
  3. Add rejection logic → test full inspection                                                 
  4. Deploy                                                                                     
                                                                                                
  The iteration happens within the generated structure rather than building toward it.          
                                                                                                
  ---                                                                                           
  Proposed Part 3: Build the Inspector (~15 min)                                                
                                                                                                
  Goal: Generate a module scaffold, implement inspection logic, test it locally.                
                                                                                                
  3.1 Generate the Module Scaffold                                                              
                                                                                                
  mkdir inspection-module && cd inspection-module                                               
  viam module generate \                                                                        
    --language go \                                                                             
    --name inspection-module \                                                                  
    --model-name inspector \                                                                    
    --resource-subtype generic-service \                                                        
    --public-namespace <your-namespace> \                                                       
    --visibility private                                                                        
                                                                                                
  Show what was generated:                                                                      
  - Explain the file structure briefly                                                          
  - Highlight the key files they'll modify: module.go (logic), cmd/cli/main.go (testing)        
                                                                                                
  Checkpoint: Students have a working scaffold.                                                 
                                                                                                
  ---                                                                                           
  3.2 Test the Connection                                                                       
                                                                                                
  The generated CLI already connects to remote machines. Students just need to:                 
                                                                                                
  1. Run viam login                                                                             
  2. Get machine address from Viam app                                                          
  3. Run: go run ./cmd/cli -host <machine-address>                                              
                                                                                                
  What they see: Connection succeeds, but DoCommand returns "not implemented" (the stub).       
                                                                                                
  Checkpoint: Connection works. Now fill in the logic.                                          
                                                                                                
  ---                                                                                           
  3.3 Add Detection Logic                                                                       
                                                                                                
  Update Config in module.go:                                                                   
  type Config struct {                                                                          
      resource.AlwaysRebuild                                                                    
      Camera        string `json:"camera"`                                                      
      VisionService string `json:"vision_service"`                                              
  }                                                                                             
                                                                                                
  Update Validate to return dependencies.                                                       
                                                                                                
  Add the Detect method:                                                                        
  func (i *Inspector) Detect(ctx context.Context) (string, float64, error) {                    
      // ... same detection logic as current Part 3.3                                           
  }                                                                                             
                                                                                                
  Wire DoCommand (just the detect case for now):                                                
  func (i *Inspector) DoCommand(ctx context.Context, req map[string]interface{})                
  (map[string]interface{}, error) {                                                             
      var cmd Command                                                                           
      mapstructure.Decode(req, &cmd)                                                            
                                                                                                
      if cmd.Detect {                                                                           
          label, confidence, err := i.Detect(ctx)                                               
          // return result                                                                      
      }                                                                                         
      return nil, fmt.Errorf("unknown command")                                                 
  }                                                                                             
                                                                                                
  Update CLI to send {"detect": true}.                                                          
                                                                                                
  Test:                                                                                         
  go run ./cmd/cli -host <machine-address>                                                      
                                                                                                
  Checkpoint: Detection works. Output shows PASS/FAIL with confidence.                          
                                                                                                
  ---                                                                                           
  3.4 Add Rejection Logic                                                                       
                                                                                                
  Configure the rejector motor in Viam app (same as current 3.4).                               
                                                                                                
  Update Config to add Rejector field.                                                          
                                                                                                
  Add reject() and Inspect() methods (same logic as current 3.5).                               
                                                                                                
  Extend DoCommand to handle inspect command.                                                   
                                                                                                
  Update CLI to accept a -cmd flag for detect vs inspect.                                       
                                                                                                
  Test both commands:                                                                           
  go run ./cmd/cli -host <machine-address> -cmd detect                                          
  go run ./cmd/cli -host <machine-address> -cmd inspect                                         
                                                                                                
  Checkpoint: Full sense-think-act loop works from laptop.                                      
                                                                                                
  ---                                                                                           
  3.5 Summary                                                                                   
                                                                                                
  - Generated module scaffold with viam module generate                                         
  - Added detection logic, tested it                                                            
  - Added rejection logic, tested full inspection                                               
  - Same iterative development pattern, less boilerplate                                        
                                                                                                
  ---                                                                                           
  Proposed Part 4: Deploy as a Module (~10 min)                                                 
                                                                                                
  Goal: Package and deploy the module to run autonomously on the machine.                       
                                                                                                
  4.1 Review What the Generator Created                                                         
                                                                                                
  The generator already created:                                                                
  - cmd/module/main.go — module entry point                                                     
  - meta.json — registry metadata                                                               
  - Model registration in init()                                                                
                                                                                                
  Quick explanation of how these pieces connect (conceptual, not writing code).                 
                                                                                                
  ---                                                                                           
  4.2 Build and Package                                                                         
                                                                                                
  make build                                                                                    
  # or: go build -o bin/inspection-module ./cmd/module                                          
                                                                                                
  The Makefile (generated) handles this. Show what it does.                                     
                                                                                                
  tar czf module.tar.gz meta.json bin/                                                          
                                                                                                
  ---                                                                                           
  4.3 Upload to Registry                                                                        
                                                                                                
  viam module upload --version 1.0.0 --platform linux/amd64 module.tar.gz                       
                                                                                                
  ---                                                                                           
  4.4 Configure on Machine                                                                      
                                                                                                
  1. Add module from registry                                                                   
  2. Add inspector service (generic)                                                            
  3. Configure attributes (camera, vision_service, rejector)                                    
  4. Save and verify in logs                                                                    
                                                                                                
  Checkpoint: Inspector runs on machine, not laptop.                                            
                                                                                                
  ---                                                                                           
  4.5 Summary                                                                                   
                                                                                                
  - Module structure was already in place from generator                                        
  - Just built, packaged, uploaded, configured                                                  
  - Inspector now runs autonomously                                                             
                                                                                                
  ---                                                                                           
  Comparison: Current vs Proposed                                                               
  ┌─────────────────────┬─────────────────────────┬───────────────────────────────┐             
  │       Aspect        │         Current         │           Proposed            │             
  ├─────────────────────┼─────────────────────────┼───────────────────────────────┤             
  │ Part 3 length       │ ~20 min                 │ ~15 min                       │             
  ├─────────────────────┼─────────────────────────┼───────────────────────────────┤             
  │ Part 4 length       │ ~20 min                 │ ~10 min                       │             
  ├─────────────────────┼─────────────────────────┼───────────────────────────────┤             
  │ Total               │ ~40 min                 │ ~25 min                       │             
  ├─────────────────────┼─────────────────────────┼───────────────────────────────┤             
  │ Boilerplate written │ All manual              │ Generated                     │             
  ├─────────────────────┼─────────────────────────┼───────────────────────────────┤             
  │ Iteration preserved │ Yes                     │ Yes                           │             
  ├─────────────────────┼─────────────────────────┼───────────────────────────────┤             
  │ DoCommand timing    │ Added in Part 4         │ Present from start            │             
  ├─────────────────────┼─────────────────────────┼───────────────────────────────┤             
  │ Educational depth   │ Deep (build everything) │ Moderate (customize scaffold) │             
  └─────────────────────┴─────────────────────────┴───────────────────────────────┘             
  ---                                                                                           
  What's Lost vs Gained                                                                         
                                                                                                
  Lost:                                                                                         
  - Step-by-step understanding of module registration internals                                 
  - The "aha" moment of seeing direct methods become DoCommand                                  
                                                                                                
  Gained:                                                                                       
  - 15 minutes shorter                                                                          
  - Follows real-world workflow                                                                 
  - Less error-prone (generated code is correct)                                                
  - Students can focus on their logic, not Viam boilerplate   