import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Contract } from './contract';

describe('Contract', () => {
  let component: Contract;
  let fixture: ComponentFixture<Contract>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Contract],
    }).compileComponents();

    fixture = TestBed.createComponent(Contract);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
