import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FinanceOfficerComponent } from './finance-officer';

describe('FinanceOfficer', () => {
  let component: FinanceOfficerComponent;
  let fixture: ComponentFixture<FinanceOfficerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FinanceOfficerComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(FinanceOfficerComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
